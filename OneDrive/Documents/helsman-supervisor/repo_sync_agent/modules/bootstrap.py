# modules/bootstrap.py

import os
import logging
from datetime import datetime
from config import README_PATH, GITIGNORE_PATH, DRY_RUN
from modules.remote import run

logger = logging.getLogger(__name__)


def create_readme():
    logger.info("[BOOTSTRAP] Create README called.")
    from config import README_PATH, DRY_RUN

    if DRY_RUN:
        logger.info("DRY_RUN: would create README at %s", README_PATH)
        return False

    try:
        os.makedirs(os.path.dirname(README_PATH), exist_ok=True)
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write("# Project\n\nBootstrapped README.\n")
        logger.info("Created README at %s", README_PATH)
        return True
    except Exception as e:
        logger.exception("Failed to create README: %s", e)
        return False


def bootstrap_repo():
    logger.info("Bootstrapping repo...")

    # Create README.md if missing
    if not os.path.exists(README_PATH):
        logger.info("Creating README.md")
        created = create_readme()
        if created:
            run(f"git add {README_PATH}")
            run('git commit -m "Add README.md"')

    # Create .gitignore if missing
    if not os.path.exists(GITIGNORE_PATH):
        logger.info("Creating .gitignore")
        default_rules = "*.log\n*.tmp\n__pycache__/\n.DS_Store\nlogs/\n"
        from config import DRY_RUN

        if DRY_RUN:
            logger.info("DRY_RUN: would write default .gitignore to %s", GITIGNORE_PATH)
        else:
            try:
                os.makedirs(os.path.dirname(GITIGNORE_PATH), exist_ok=True)
                with open(GITIGNORE_PATH, "w", encoding="utf-8") as f:
                    f.write(default_rules)
                run(f"git add {GITIGNORE_PATH}")
                run('git commit -m "Add default .gitignore"')
            except Exception as e:
                logger.exception("Failed to create .gitignore: %s", e)

    logger.info("Bootstrap complete.")
