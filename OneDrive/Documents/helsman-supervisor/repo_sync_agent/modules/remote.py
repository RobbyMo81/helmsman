# modules/remote.py

import os
import subprocess
import logging
from config import REPO_PATH, REMOTE_URL, BRANCH, DRY_RUN

logger = logging.getLogger(__name__)


def run(cmd, check=False):
    logger.debug("[REMOTE] %s", cmd)
    if DRY_RUN:
        logger.info("DRY_RUN: command not executed: %s", cmd)
        return 0
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        logger.error("Command failed: %s", cmd)
        raise RuntimeError(f"Command failed: {cmd}")
    return result.returncode


def set_remote(remote_url=None):
    """Configure the repository remote. If remote_url is None use REMOTE_URL from config."""
    target = remote_url if remote_url else REMOTE_URL
    logger.info("[SYNC] Setting remote to %s", target)
    os.chdir(REPO_PATH)

    if not os.path.exists(os.path.join(REPO_PATH, ".git")):
        logger.info("Initializing Git repository at %s", REPO_PATH)
        run("git init", check=True)

    # Remove existing origin if present
    run("git remote remove origin || true")
    run(f"git remote add origin {target}")
    logger.info("Remote set to %s on branch '%s'", target, BRANCH)
