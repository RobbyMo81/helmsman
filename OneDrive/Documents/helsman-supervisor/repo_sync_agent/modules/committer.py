# modules/committer.py

import os
from datetime import datetime, timezone
import logging
from config import REPO_PATH, BRANCH, DRY_RUN
from modules.remote import run

logger = logging.getLogger(__name__)


def stage_and_commit():
    logger.info("Staging and committing changes...")
    os.chdir(REPO_PATH)

    # Stage all changes
    run("git add .")

    # Commit with UTC timestamp
    timestamp = datetime.now(timezone.utc).isoformat()
    commit_cmd = (
        f'git commit -m "Sync commit @ {timestamp}" || echo "Nothing to commit"'
    )
    run(commit_cmd)


def commit_changes(branch="main", dry_run=False):
    """High-level commit flow: stage, commit, and push changes.

    If DRY_RUN or dry_run=True, do not push.
    """
    logger.info(
        "[COMMIT] Commit changes for branch=%s, dry_run=%s, config.DRY_RUN=%s",
        branch,
        dry_run,
        DRY_RUN,
    )
    # Stage and commit
    stage_and_commit()

    # Push if allowed
    if DRY_RUN or dry_run:
        logger.info("DRY_RUN: skipping push")
        return

    push_to_github()


def push_to_github():
    logger.info("Pushing to GitHub...")
    run(f"git push -u origin {BRANCH}")
    logger.info("Pushed to branch '%s'", BRANCH)
