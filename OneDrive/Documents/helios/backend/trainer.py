"""
Helios Trainer - Model Training and Management System
Handles the training pipeline, data preprocessing, and model evaluation.
"""

import torch
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime, timedelta
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from agent import MLPowerballAgent, PowerballNet
from memory_store import MemoryStore

logger = logging.getLogger(__name__)

class TrainingConfig:
    """Configuration class for training parameters."""
    
    def __init__(self,
                 epochs: int = 100,
                 learning_rate: float = 0.001,
                 batch_size: int = 32,
                 validation_split: float = 0.2,
                 early_stopping_patience: int = 10,
                 min_delta: float = 0.001,
                 save_best_only: bool = True,
                 sequence_length: int = 50):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.validation_split = validation_split
        self.early_stopping_patience = early_stopping_patience
        self.min_delta = min_delta
        self.save_best_only = save_best_only
        self.sequence_length = sequence_length

class DataPreprocessor:
    """Handles data loading, cleaning, and preprocessing for lottery data."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_columns = []
    
    def load_historical_data(self, data_source: str) -> pd.DataFrame:
        """
        Load historical lottery data from various sources.
        
        Args:
            data_source: Path to data file or URL
            
        Returns:
            DataFrame with historical lottery data
        """
        try:
            if data_source.endswith('.csv'):
                df = pd.read_csv(data_source)
            elif data_source.endswith('.json'):
                df = pd.read_json(data_source)
            elif data_source.startswith('http'):
                # Handle web data sources
                df = pd.read_csv(data_source)
            else:
                raise ValueError(f"Unsupported data source format: {data_source}")
            
            logger.info(f"Loaded {len(df)} records from {data_source}")
            return self._validate_and_clean(df)
            
        except Exception as e:
            logger.error(f"Failed to load data from {data_source}: {str(e)}")
            raise
    
    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean the loaded data."""
        required_columns = ['draw_date', 'white_ball_1', 'white_ball_2', 'white_ball_3', 
                           'white_ball_4', 'white_ball_5', 'powerball']
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Convert date column
        df['draw_date'] = pd.to_datetime(df['draw_date'])
        
        # Sort by date
        df = df.sort_values('draw_date').reset_index(drop=True)
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['draw_date']).reset_index(drop=True)
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate records")
        
        return df
    
    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add engineered features to the dataset."""
        logger.info("Adding engineered features...")
        
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Basic statistical features
        white_ball_cols = ['white_ball_1', 'white_ball_2', 'white_ball_3', 'white_ball_4', 'white_ball_5']
        
        # Sum of white balls
        df['white_sum'] = df[white_ball_cols].sum(axis=1)
        
        # Number of even/odd white balls
        df['white_even_count'] = (df[white_ball_cols] % 2 == 0).sum(axis=1)
        df['white_odd_count'] = 5 - df['white_even_count']
        
        # Range (max - min) of white balls
        df['white_range'] = df[white_ball_cols].max(axis=1) - df[white_ball_cols].min(axis=1)
        
        # Consecutive numbers feature
        for i in range(len(df)):
            balls = sorted(df[white_ball_cols].iloc[i].values)
            consecutive = 0
            for j in range(len(balls) - 1):
                if balls[j+1] == balls[j] + 1:
                    consecutive += 1
            df.loc[i, 'consecutive_count'] = consecutive
        
        # Time-based features
        df['day_of_week'] = df['draw_date'].dt.dayofweek
        df['month'] = df['draw_date'].dt.month
        df['year'] = df['draw_date'].dt.year
        
        # Rolling statistics
        for window in [5, 10, 20]:
            df[f'white_sum_rolling_mean_{window}'] = df['white_sum'].rolling(window=window).mean()
            df[f'powerball_rolling_mean_{window}'] = df['powerball'].rolling(window=window).mean()
        
        # Fill NaN values from rolling statistics
        df = df.bfill().ffill()
        
        logger.info(f"Added features. Dataset now has {df.shape[1]} columns")
        return df


class ModelTrainer:
    """Main trainer class for managing model training workflows."""
    
    def __init__(self, 
                 model_dir: str = "models",
                 config: Optional[TrainingConfig] = None,
                 device: Optional[str] = None,
                 memory_store: Optional[MemoryStore] = None):
        """
        Initialize the trainer.
        
        Args:
            model_dir: Directory to save trained models
            config: Training configuration
            device: PyTorch device
            memory_store: Memory store for persistence
        """
        self.model_dir = model_dir
        self.config = config or TrainingConfig()
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.memory_store = memory_store
        
        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize components
        self.preprocessor = DataPreprocessor()
        self.agent: Optional[MLPowerballAgent] = None
        self.training_journal = []
        
        logger.info(f"Trainer initialized on device: {self.device}")
    
    def start_training_job(self,
                          model_name: str,
                          data_source: str,
                          config_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start a new training job.
        
        Args:
            model_name: Name for the trained model
            data_source: Path to training data
            config_override: Override default training configuration
            
        Returns:
            Training job information
        """
        job_id = f"job_{model_name}_{int(datetime.now().timestamp())}"
        
        logger.info(f"Starting training job {job_id} for model {model_name}")
        
        # Override config if provided
        if config_override:
            for key, value in config_override.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        # Initialize training journal entry
        job_info = {
            'job_id': job_id,
            'model_name': model_name,
            'status': 'started',
            'start_time': datetime.now().isoformat(),
            'config': self.config.__dict__.copy(),
            'data_source': data_source,
            'progress': 0,
            'current_epoch': 0,
            'best_loss': float('inf'),
            'training_logs': []
        }
        
        self.training_journal.append(job_info)
        
        try:
            # Load and preprocess data
            self._update_job_status(job_id, 'loading_data', 10)
            historical_data = self.preprocessor.load_historical_data(data_source)
            
            # Add engineered features
            self._update_job_status(job_id, 'preprocessing', 20)
            historical_data = self.preprocessor.add_features(historical_data)
            
            # Initialize agent
            self._update_job_status(job_id, 'initializing_model', 30)
            self.agent = MLPowerballAgent(
                model_dir=self.model_dir,
                sequence_length=self.config.sequence_length,
                device=self.device
            )
            
            # Start training
            self._update_job_status(job_id, 'training', 40)
            model_path = self._train_with_monitoring(job_id, historical_data)
            
            # Complete job
            self._update_job_status(job_id, 'completed', 100)
            
            job_info = self._get_job_info(job_id)
            if job_info:
                job_info['end_time'] = datetime.now().isoformat()
                job_info['model_path'] = model_path
                job_info['final_metrics'] = self._calculate_final_metrics()
            
            logger.info(f"Training job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Training job {job_id} failed: {str(e)}")
            self._update_job_status(job_id, 'failed', 0, error=str(e))
            raise e
        
        return job_info or {}
    
    def _train_with_monitoring(self, job_id: str, historical_data: pd.DataFrame) -> str:
        """Train the model with progress monitoring."""
        if not self.agent:
            raise RuntimeError("Agent not initialized")
        
        # Custom training loop with monitoring
        (X_white, X_powerball), (y_white, y_powerball) = self.agent.prepare_data(historical_data)
        
        # Initialize training components
        optimizer = torch.optim.Adam(self.agent.model.parameters(), lr=self.config.learning_rate)
        criterion = torch.nn.CrossEntropyLoss()
        
        best_loss = float('inf')
        patience_counter = 0
        epoch = 0
        
        self.agent.model.train()
        
        for epoch in range(self.config.epochs):
            optimizer.zero_grad()
            
            # Forward pass
            outputs = self.agent.model(X_white, X_powerball)
            
            # Calculate losses
            white_losses = []
            for i in range(5):  # 5 white balls
                white_loss = criterion(outputs['white_balls'][i], y_white[:, i])
                white_losses.append(white_loss)
            
            powerball_loss = criterion(outputs['powerball'], y_powerball)
            total_loss = sum(white_losses) + powerball_loss
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            
            current_loss = float(total_loss.item())
            
            # Log training progress
            log_entry = {
                'epoch': epoch + 1,
                'loss': current_loss,
                'white_losses': [float(loss.item()) for loss in white_losses],
                'powerball_loss': float(powerball_loss.item()),
                'timestamp': datetime.now().isoformat()
            }
            
            job_info = self._get_job_info(job_id)
            if job_info:
                job_info['training_logs'].append(log_entry)
                job_info['current_epoch'] = epoch + 1
            
            # Update progress
            progress = 40 + int((epoch + 1) / self.config.epochs * 50)  # 40-90%
            self._update_job_status(job_id, 'training', progress)
            
            # Early stopping logic
            if current_loss < best_loss - self.config.min_delta:
                best_loss = current_loss
                patience_counter = 0
                if job_info:
                    job_info['best_loss'] = best_loss
                
                # Save best model if configured
                if self.config.save_best_only:
                    # Could save checkpoint here
                    pass
            else:
                patience_counter += 1
            
            # Log progress
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch + 1}/{self.config.epochs}, Loss: {current_loss:.4f}")
            
            # Early stopping
            if patience_counter >= self.config.early_stopping_patience:
                logger.info(f"Early stopping triggered at epoch {epoch + 1}")
                break
        
        # Update agent's training history and metadata
        job_info = self._get_job_info(job_id)
        if self.agent and job_info:
            if hasattr(self.agent, 'training_history'):
                self.agent.training_history = job_info['training_logs']
            if hasattr(self.agent, 'metadata'):
                self.agent.metadata['total_epochs'] = epoch + 1
                self.agent.metadata['best_loss'] = best_loss
                self.agent.metadata['training_completed'] = True
        
        # Save the final model
        model_path = f"{self.model_dir}/{job_id}_final.pth"
        if self.agent and self.agent.model:
            torch.save(self.agent.model.state_dict(), model_path)
            logger.info(f"Model saved to {model_path}")
        
        return model_path
    
    def _update_job_status(self, job_id: str, status: str, progress: int, error: Optional[str] = None):
        """Update the status of a training job."""
        job_info = self._get_job_info(job_id)
        if job_info:
            job_info['status'] = status
            job_info['progress'] = progress
            if error:
                job_info['error'] = error
            job_info['last_updated'] = datetime.now().isoformat()
    
    def _get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information by ID."""
        for job in self.training_journal:
            if job['job_id'] == job_id:
                return job
        return None
    
    def _calculate_final_metrics(self) -> Dict[str, Any]:
        """Calculate final training metrics."""
        if not self.agent or not hasattr(self.agent, 'training_history') or not self.agent.training_history:
            return {}
        
        training_losses = [entry['loss'] for entry in self.agent.training_history]
        
        return {
            'final_loss': training_losses[-1] if training_losses else 0.0,
            'min_loss': min(training_losses) if training_losses else 0.0,
            'avg_loss': sum(training_losses) / len(training_losses) if training_losses else 0.0,
            'total_epochs': len(training_losses),
            'convergence_epoch': None  # Could implement convergence detection
        }
    
    def get_training_journal(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get training history, optionally filtered by model name."""
        if model_name:
            return [job for job in self.training_journal if job['model_name'] == model_name]
        return self.training_journal
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a training job."""
        return self._get_job_info(job_id)
    
    def evaluate_model(self, model_name: str, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate a trained model on test data."""
        if not self.agent or not self.agent.model:
            raise ValueError("No trained model available for evaluation")
        
        logger.info(f"Evaluating model {model_name}")
        
        # Preprocess test data
        test_data = self.preprocessor.add_features(test_data)
        (X_white_test, X_powerball_test), (y_white_test, y_powerball_test) = self.agent.prepare_data(test_data)
        
        self.agent.model.eval()
        with torch.no_grad():
            outputs = self.agent.model(X_white_test, X_powerball_test)
            
            # Calculate accuracy for each position
            white_accuracies = []
            for i in range(5):
                predicted = torch.argmax(outputs['white_balls'][i], dim=1)
                actual = y_white_test[:, i]
                accuracy = (predicted == actual).float().mean().item()
                white_accuracies.append(accuracy)
            
            # Powerball accuracy
            powerball_predicted = torch.argmax(outputs['powerball'], dim=1)
            powerball_accuracy = (powerball_predicted == y_powerball_test).float().mean().item()
        
        metrics = {
            'white_ball_accuracies': white_accuracies,
            'average_white_accuracy': sum(white_accuracies) / len(white_accuracies),
            'powerball_accuracy': powerball_accuracy,
            'overall_accuracy': (sum(white_accuracies) + powerball_accuracy) / 6,
            'evaluation_timestamp': datetime.now().isoformat()
        }
        
        return metrics
    
    def get_all_training_sessions(self) -> List[Dict[str, Any]]:
        """Get all training sessions from memory store."""
        if not self.memory_store:
            return self.training_journal
        
        # This would query all training sessions from the database
        # For now, return the in-memory journal
        return self.training_journal
    
    def get_training_progress(self, job_id: str) -> Dict[str, Any]:
        """Get detailed training progress for a job."""
        job_info = self._get_job_info(job_id)
        if not job_info:
            return {}
        
        progress_info = {
            'job_id': job_id,
            'status': job_info.get('status', 'unknown'),
            'progress': job_info.get('progress', 0),
            'current_epoch': job_info.get('current_epoch', 0),
            'total_epochs': self.config.epochs,
            'best_loss': job_info.get('best_loss', float('inf')),
            'training_logs': job_info.get('training_logs', []),
            'start_time': job_info.get('start_time'),
            'last_updated': job_info.get('last_updated')
        }
        
        return progress_info
