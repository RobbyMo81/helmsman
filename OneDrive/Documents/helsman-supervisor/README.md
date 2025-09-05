# Helmsman Supervisor CLI

Install once, supervise many local projects: bootstrap venv, run preflight health checks, test, launch Streamlit UI and headless Torch jobs, capture logs, and emit machine-readable supervision reports.

## The following files are part of the Helmsman Supervisor project:

- `helmsman.py`: The main entry point for the CLI.
- `supervisor.py`: The core logic for supervising projects.
- `utils.py`: Utility functions used throughout the project.
- `config.yaml`: Configuration file for the supervisor.
- `README.md`: This README file.

## Dependencies

Contributors: the authoritative dependency list is in `pyproject.toml` for packaging; a convenience `requirements.txt` file is also provided for quick pip installs. To install the runtime dependencies into your active virtual environment:

```powershell
python -m pip install -r requirements.txt
```

If you're working with packaging or building wheels, prefer `pyproject.toml` and modern tools (pip, build, or poetry).
