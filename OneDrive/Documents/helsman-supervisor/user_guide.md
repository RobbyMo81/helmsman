# Helmsman Supervisor User Guide

1. **Human-readable**: Markdown format for your repos/docs.
2. **Machine-readable**: JSON schema of commands, arguments, and outputs so agents can parse and orchestrate.

---

## 📖 Helmsman User Manual (Markdown)

## Overview

Helmsman is a lightweight, single-host supervisor CLI for local ML analyzers (Streamlit UI + Torch headless). It manages:

- Virtualenv bootstrap & dependency install
- Preflight health checks (Python, Torch, CUDA, ports)
- Test runs (pytest)
- Launch & supervise processes
- Watch TUI with live health + log tails
- Project registry (`~/.config/helmsman/registry.yaml`)
- Machine-readable reports

---

## Installation

```bash
git clone https://github.com/your-org/helmsman.git
cd helmsman
python -m venv .venv && . .venv/bin/activate
pip install -e .[tui,streamlit,test]
```

---

## Commands

### `helmsman init-config`

Generate `.helmsman.yaml` in current project with default config.

### `helmsman bootstrap [--config PATH]`

- Create `venv` if missing.
- Install requirements from config.

### `helmsman health [--config PATH]`

Run preflight checks. Writes `artifacts/reports/health.json`.

### `helmsman test [--config PATH]`

Run pytest using project’s venv.

### `helmsman run streamlit [--config PATH]`

Launch Streamlit Data Analyzer.

### `helmsman run torch [--infile PATH] [--device cpu|cuda] [--max-batch N]`

Launch Torch analyzer with options.

### `helmsman status`

Show running processes with PID and logs.

### `helmsman stop [name|all]`

Stop one or all supervised processes.

### `helmsman report`

Emit JSON (`supervision_report_*.json`) and Markdown (`supervision_report.md`) with health, procs, log tails.

### `helmsman watch`

Live TUI: health + streamlit/torch/pytest logs.

### Registry

- `helmsman register NAME PATH` → save project
- `helmsman list` → list registered projects
- `helmsman open NAME` → print path for NAME

---

## Files & Artifacts

- `artifacts/logs/*.log` → per-process logs
- `artifacts/reports/*.json` → structured reports
- `artifacts/reports/supervision_report.md` → human summary
- `~/.config/helmsman/registry.yaml` → registry of projects

---

## 🤖 Machine-Readable Spec (JSON)

```json
{
  "commands": {
    "init-config": { "args": [], "output": [".helmsman.yaml file"] },
    "bootstrap": {
      "args": ["--config PATH"],
      "output": ["venv created", "deps installed"]
    },
    "health": {
      "args": ["--config PATH"],
      "output": ["artifacts/reports/health.json"]
    },
    "test": {
      "args": ["--config PATH"],
      "output": ["pytest exit code", "artifacts/logs/pytest.log"]
    },
    "run:streamlit": {
      "args": ["--config PATH"],
      "output": ["PID", "artifacts/logs/streamlit.log"]
    },
    "run:torch": {
      "args": ["--infile PATH", "--device cpu|cuda", "--max-batch N"],
      "output": ["PID", "artifacts/logs/torch.log"]
    },
    "status": { "args": [], "output": ["running processes list"] },
    "stop": { "args": ["name|all"], "output": ["stopped processes"] },
    "report": {
      "args": [],
      "output": ["supervision_report_*.json", "supervision_report.md"]
    },
    "watch": { "args": [], "output": ["TUI live screen"] },
    "register": { "args": ["NAME PATH"], "output": ["registry.yaml updated"] },
    "list": { "args": [], "output": ["registry entries"] },
    "open": { "args": ["NAME"], "output": ["PATH of project"] }
  },
  "artifacts": {
    "logs": "artifacts/logs/*.log",
    "reports": "artifacts/reports/*.json",
    "registry": "~/.config/helmsman/registry.yaml"
  }
}
```

---

## End of Instructions
