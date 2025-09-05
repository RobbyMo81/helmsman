# modules/audit.py

import os
import subprocess
import logging
from config import REPO_PATH, COMMIT_LOG_PATH, DRY_RUN

logger = logging.getLogger(__name__)


def audit_repo():
    """Run git log and write to commit log path. Respects DRY_RUN."""
    logger.info("Auditing commit history...")
    cwd = os.getcwd()
    try:
        os.chdir(REPO_PATH)
    except Exception:
        logger.exception("Could not change directory to %s; aborting audit", REPO_PATH)
        return

    log_cmd = "git log --oneline --decorate --graph --all"
    logger.debug("> %s", log_cmd)
    if DRY_RUN:
        logger.info("DRY_RUN: skipping git log execution")
        os.chdir(cwd)
        return

    try:
        result = subprocess.run(
            log_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output = result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        output = f"Error running git log: {e}"

    try:
        os.makedirs(os.path.dirname(COMMIT_LOG_PATH), exist_ok=True)
        with open(COMMIT_LOG_PATH, "w", encoding="utf-8") as f:
            f.write(output)
        logger.info("Commit history written to %s", COMMIT_LOG_PATH)
    except Exception as e:
        logger.exception("Failed to write commit log: %s", e)
    finally:
        os.chdir(cwd)
