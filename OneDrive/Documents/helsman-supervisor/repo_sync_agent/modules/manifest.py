# modules/manifest.py

from datetime import datetime, timezone
import logging
from config import MANIFEST_PATH, REMOTE_URL, BRANCH, DRY_RUN

logger = logging.getLogger(__name__)


def generate_manifest(output=None):
    """Generate a simple sync manifest.

    If `output` is provided, write to that path, otherwise use MANIFEST_PATH.
    Respects the DRY_RUN flag from config.
    """
    target = output if output else MANIFEST_PATH
    logger.info("Generating sync manifest...")
    timestamp = datetime.now(timezone.utc).isoformat()
    content = (
        f"Repo synced to {REMOTE_URL}\n"
        f"Branch: {BRANCH}\n"
        f"Timestamp (UTC): {timestamp}\n"
    )

    if not DRY_RUN:
        # Ensure parent dir exists
        try:
            from pathlib import Path

            Path(target).parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)

    logger.info("Manifest written to %s", target)
