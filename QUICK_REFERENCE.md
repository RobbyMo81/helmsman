# Quick Reference Guide

## Project Structure at a Glance

```
helmsman (root)
├── OneDrive/Documents/
│   ├── helios/                    ← Main full-stack app
│   │   ├── backend/ (Python)
│   │   ├── components/ (React)
│   │   ├── services/ (API layer)
│   │   ├── tests/ (Frontend tests)
│   │   └── package.json
│   │
│   ├── helsman-supervisor/        ← CLI project manager
│   │   ├── helmsman/ (Python pkg)
│   │   ├── repo_sync_agent/
│   │   ├── pyproject.toml
│   │   └── setup.py
│   │
│   └── commitment-of-traders/    ← Data directory
│
├── .git/
├── .gitignore
└── CODEBASE_ANALYSIS.md          ← This analysis
```

## Quick Stats

| Metric | Value |
|--------|-------|
| **Primary Language** | Python (60%) + TypeScript (40%) |
| **Main Framework** | Flask (Backend) + React 19 (Frontend) |
| **Development Phase** | Phase 4 (Cross-model analytics) |
| **Current Branch** | `claude/init-project-012...` |
| **Build Tool** | Vite 6.2 (Frontend), setuptools (Backend) |
| **Container Runtime** | Docker Compose v3.8 |
| **Package Managers** | npm (frontend), pip (backend) |
| **Testing Frameworks** | pytest (backend), Jest/manual (frontend) |
| **Total Python Modules** | 20+ in Helios, 6+ in Supervisor |
| **React Components** | 15+ custom components |
| **Database** | SQLite (helios_memory.db) |

## Core Technologies

### Frontend Stack
- **React** 19.1.0
- **TypeScript** 5.7.2
- **Vite** 6.2.0 (bundler)
- **Material-UI** 7.2.0
- **Chart.js** / **Recharts** (visualizations)
- **Emotion** (CSS-in-JS)
- **Google Generative AI API**

### Backend Stack
- **Flask** 3.0.0
- **PyTorch** 2.7.1
- **scikit-learn**, **NumPy**, **Pandas**
- **SQLite** (persistent memory)
- **Gunicorn** (WSGI server)
- **pytest** (testing)

### Infrastructure
- **Docker** & **Docker Compose**
- **Nginx** (frontend proxy)
- **Git hooks** (pre-commit)
- **Black** (Python formatter)
- **Prettier** (JS/TS formatter)

## Key Components

### Backend (Helios)
| Component | Purpose | Size |
|-----------|---------|------|
| `agent.py` | PowerballNet neural network | 17.4KB |
| `memory_store.py` | SQLite persistence layer | 37.4KB |
| `trainer.py` | Model training orchestration | 554 lines |
| `metacognition.py` | Self-reflection engine | 23.2KB |
| `decision_engine.py` | Goal-based decisions | 30.8KB |
| `cross_model_analytics.py` | Multi-model comparison | 30.8KB |
| `server.py` | Flask REST API | 49.4KB |

### Frontend (Helios)
| Component | Purpose |
|-----------|---------|
| `App.tsx` | Main container (513 lines) |
| `Sidebar.tsx` | Navigation |
| `TrainingDashboard.tsx` | Progress visualization |
| `MetacognitiveDashboard.tsx` | Reasoning display |
| `CrossModelAnalytics.tsx` | Model comparison |
| `StressTestComponent.tsx` | Load testing UI |

### CLI (Helmsman Supervisor)
| Module | Purpose | Size |
|--------|---------|------|
| `cli.py` | Command-line interface | 4.8KB |
| `config.py` | YAML config parser | 4.1KB |
| `runtime.py` | Bootstrap & health checks | 4.6KB |
| `process.py` | Lifecycle management | 1.2KB |
| `report.py` | Report generation | 2.0KB |

## Common Commands

### Development

```bash
# Frontend only
cd OneDrive/Documents/helios
npm install
npm run dev                    # http://localhost:5173

# Backend only
npm run python:setup          # Setup venv
npm run python:dev            # http://localhost:5001

# Full stack (manual)
# Terminal 1: npm run python:dev
# Terminal 2: npm run dev

# Full stack (Docker)
npm run docker:build
npm run docker:dev
npm run docker:logs
npm run docker:down
```

### Testing

```bash
# Stress tests
npm run stress-test

# Backend unit tests
npm run python:test

# Frontend browser tests
# Open http://localhost:5173, press F12, run testConnection()
```

### Project Management (Helmsman)

```bash
cd OneDrive/Documents/helsman-supervisor

# Initialize
helmsman init-config

# Pre-flight checks
helmsman health
helmsman bootstrap

# Running services
helmsman run streamlit        # Launch Streamlit UI
helmsman run torch            # Run PyTorch jobs

# Status & reporting
helmsman status
helmsman report
```

## Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `package.json` | npm deps & scripts | helios/ |
| `tsconfig.json` | TypeScript config | helios/ |
| `vite.config.ts` | Vite build config | helios/ |
| `requirements.txt` | Python dependencies | helios/backend/ |
| `pytest.ini` | Pytest configuration | helios/backend/ |
| `docker-compose.yml` | Multi-container setup | helios/ |
| `pyproject.toml` | Python package config | helsman-supervisor/ |
| `.pre-commit-config.yaml` | Git hooks | helsman-supervisor/ |

## Ports Used

| Service | Port | Environment |
|---------|------|-------------|
| React Dev (Vite) | 5173/5174 | Dev |
| Flask Backend | 5001 | All |
| Frontend (Nginx) | 80, 443 | Production |
| Frontend Dev (Docker) | 5173 | Dev Docker |

## Environment Variables

### Frontend (.env.development / .env.production)
- `VITE_API_HOST`: Backend API hostname
- `VITE_API_PORT`: Backend API port
- `VITE_API_PROTOCOL`: HTTP or HTTPS
- `GEMINI_API_KEY`: Google Generative AI key

### Backend (.env.example)
- `FLASK_ENV`: development/production
- `FLASK_DEBUG`: true/false
- Database credentials (if applicable)

## Testing

- **Backend**: pytest (8 test suites, 2300+ lines)
- **Frontend**: Manual + stress tests
- **Integration**: Full-stack E2E tests
- **Stress Tests**: Load testing with custom runner

## Git Status

- **Current Branch**: `claude/init-project-012QPE4zPFRkQmtS7uD7HGf1`
- **Status**: Clean (no uncommitted changes)
- **Recent Commits**:
  - docs: add comprehensive repository architecture analysis
  - fix: disable UTF-8 encoding hook due to monorepo path issue
  - fix: comment out Documents/ pattern to allow project tracking
  - feat: add comprehensive .gitignore for user home directory repository

## Phase History

- ✓ **Phase 1**: Foundation
- ✓ **Phase 2**: Comprehensive testing
- ✓ **Phase 3**: Core functionality
- ✓ **Phase 4**: Cross-model analytics (CURRENT)

## Key URLs & Resources

- Frontend Dev: http://localhost:5173
- Backend Dev: http://localhost:5001
- Docker Logs: `npm run docker:logs`
- Documentation: See *.md files in helios/

---

**Last Updated**: Nov 15, 2025
**Analysis Depth**: Very Thorough
