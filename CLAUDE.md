# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **multi-project monorepo** containing two main projects:

1. **Helios** (`OneDrive/Documents/helios/`) - Full-stack Powerball lottery anomaly detection application
   - Frontend: React 19 + TypeScript + Vite + Material-UI
   - Backend: Flask + PyTorch for ML-based pattern detection
   - Database: SQLite for persistent memory and model metadata

2. **Helmsman Supervisor** (`OneDrive/Documents/helsman-supervisor/`) - CLI tool for managing ML projects and local deployments

## Common Commands

### Helios Development

All commands should be run from `OneDrive/Documents/helios/`:

```bash
# Frontend development
npm install              # Install dependencies
npm run dev              # Start Vite dev server (http://localhost:5173)
npm run build            # Production build
npm run preview          # Preview production build

# Backend development (Python virtual environment)
npm run python:setup     # Create virtual environment and install dependencies
npm run python:dev       # Run Flask development server (http://localhost:5001)
npm run python:test      # Run pytest suite (8+ test modules)

# Full-stack development (manual)
# Terminal 1: npm run python:dev
# Terminal 2: npm run dev

# Docker (full stack)
npm run docker:build     # Build Docker images
npm run docker:dev       # Start with development profile
npm run docker:up        # Start all services (production mode)
npm run docker:logs      # View container logs
npm run docker:down      # Stop all services

# Testing
npm run stress-test      # Run stress tests
```

### Helmsman Supervisor

Commands for the supervisor CLI (from `OneDrive/Documents/helsman-supervisor/`):

```bash
helmsman init-config     # Create configuration template
helmsman bootstrap       # Setup environment and dependencies
helmsman health          # Check system health
helmsman run streamlit   # Launch Streamlit UI
helmsman run torch       # Run PyTorch jobs
helmsman report          # Generate supervision report
```

## Architecture

### Helios Backend (Python/Flask)

The backend follows a **layered architecture with specialized AI components**:

1. **PowerballNet** (`backend/agent.py`) - Custom PyTorch neural network with:
   - Separate pathways for white balls (1-69) and Powerball (1-26)
   - Attention mechanism for pattern recognition
   - Multi-head output architecture

2. **Memory Store** (`backend/memory_store.py`) - SQLite-based persistence layer:
   - Stores model metadata, training journals, and decision history
   - Thread-safe database operations
   - Schema: `helios_memory.db` with tables for memories, metadata, and context

3. **Trainer** (`backend/trainer.py`) - Model training orchestration:
   - Manages training configuration and epochs
   - Handles model serialization to `backend/models/`
   - Loss computation and optimization

4. **Metacognitive Engine** (`backend/metacognition.py`) - Self-reflection system:
   - Analyzes model decisions and provides reasoning
   - Evaluates model performance and confidence
   - Generates explanations for predictions

5. **Decision Engine** (`backend/decision_engine.py`) - Goal-based decision making:
   - Strategic planning and execution
   - Integrates with memory store for context
   - Provides decision justifications

6. **Cross-Model Analytics** (`backend/cross_model_analytics.py`) - Phase 4 feature:
   - Compares multiple model predictions
   - Detects consensus and divergence patterns
   - Provides meta-analysis of model behavior

7. **Server** (`backend/server.py`) - Flask REST API:
   - CORS-enabled for frontend integration
   - Dynamic component initialization
   - Health check endpoints
   - Model management routes

### Helios Frontend (React/TypeScript)

Component hierarchy:

- `App.tsx` (513 lines) - Main container with state management
- `Sidebar.tsx` - Navigation and UI controls
- `TrainingDashboard.tsx` - Real-time training progress visualization
- `MetacognitiveDashboard.tsx` - Model reasoning and reflection display
- `CrossModelAnalytics.tsx` - Multi-model comparison interface
- `StressTestComponent.tsx` - System stress testing UI
- `ResultsPanel.tsx` - Analysis results display
- `FileUploader.tsx` - Data input interface

### Key Patterns

**Memory Persistence**: The backend uses SQLite (`helios_memory.db`) to maintain state across sessions. When working with memory-related features, ensure database operations are thread-safe and properly transaction-wrapped.

**Metacognition System**: The application has self-reflective capabilities. When debugging or extending AI features, consider how the metacognition engine will interpret and explain the behavior.

**Phase-Based Development**: The project follows a phased implementation approach (currently Phase 4). See `PHASE_*_COMPLETE.md` files for historical context.

## Testing

### Backend Testing (pytest)

Test suites in `backend/tests/`:

```bash
# Run all tests
npm run python:test

# Run specific test file
cd backend && venv/Scripts/activate && pytest tests/test_memory_store.py -v
```

Key test modules:
- `test_memory_store.py` (607 lines) - Memory persistence tests
- `test_integration_basic.py` (443 lines) - Basic integration tests
- `test_integration_phase_4.py` (554 lines) - Phase 4 functionality
- `test_phase3_core_functions.py` (546 lines) - Core logic validation
- `test_phase_4_analytics.py` (562 lines) - Cross-model analytics
- `test_server_unit.py` (231 lines) - Server endpoint tests

### Frontend Testing

```bash
# Stress tests
npm run stress-test

# Manual browser testing
# 1. Open http://localhost:5173 (or :5174 if 5173 is in use)
# 2. Open browser console (F12)
# 3. Run testConnection() to verify backend connectivity
```

## Environment Configuration

### Frontend Environment Variables

Create `.env.development` or `.env.production`:

```
VITE_API_HOST=localhost
VITE_API_PORT=5001
VITE_API_PROTOCOL=http
GEMINI_API_KEY=your_api_key_here
```

### Backend Environment Variables

The backend uses Flask's default environment configuration. For production, set:

```
FLASK_ENV=production
FLASK_DEBUG=false
```

## Development Notes

### Port Configuration

- **Frontend Dev (Vite)**: 5173 (or 5174 if 5173 is in use)
- **Backend (Flask)**: 5001
- **Frontend Production (Nginx)**: 80, 443
- **Frontend Dev (Docker)**: 5173

### Virtual Environment

The Python virtual environment is located at `backend/venv/`. On Windows, use `npm run python:setup` to create it automatically. The setup scripts handle platform differences (Windows/Unix).

### Docker Profiles

- Default: Production-ready stack with Nginx serving built frontend
- `--profile dev`: Development mode with Vite HMR

### Code Formatting

- **Python**: Black formatter (configured in `.pre-commit-config.yaml`)
- **JavaScript/TypeScript**: Prettier (configured in `.prettierrc.json`)

Pre-commit hooks are configured to automatically format code before commits.

### Database Location

The SQLite database (`helios_memory.db`) is created in the `backend/` directory. It contains:
- `memories` table - Timestamped memory entries
- `metadata` table - Model and system metadata
- `future_context` table - Planned actions and predictions

## Important Files

- `backend/server.py` - Main Flask application entry point
- `App.tsx` - Main React application component
- `types.ts` - TypeScript type definitions for the entire frontend
- `constants.ts` - Frontend configuration constants
- `vite.config.ts` - Vite build configuration with path aliases
- `docker-compose.yml` - Multi-container orchestration
- `backend/requirements.txt` - Python dependencies

## Documentation

Comprehensive documentation exists for various aspects:

- `FULL_STACK_INTEGRATION.md` - How frontend and backend integrate
- `PYTHON_VENV_SETUP.md` - Detailed virtual environment setup
- `DOCKER_SETUP.md` - Docker deployment guide
- `STRESS_TEST_GUIDE.md` - Performance testing procedures
- `PHASE_*_COMPLETE.md` - Historical phase completion reports
- `SYSTEM_SCHEMA.md` - System architecture documentation

## Helmsman Supervisor Architecture

The supervisor CLI (`helsman-supervisor/`) is a lightweight project management tool with:

- `helmsman/cli.py` - Command-line interface entry point
- `helmsman/config.py` - YAML configuration parser and validation
- `helmsman/runtime.py` - Bootstrap, health checks, process management
- `helmsman/process.py` - Process lifecycle management
- `helmsman/report.py` - Supervision report generation
- `repo_sync_agent/` - Repository synchronization module

Configuration is driven by YAML files validated against JSON schemas in `schemas/`.
