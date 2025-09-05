# modules/cleaner.py

import os
import logging
from config import REPO_PATH, MAX_FILE_SIZE_MB, DRY_RUN

logger = logging.getLogger(__name__)


def clean_repo(threshold=100):
    """Scan repository for files larger than `threshold` MB and remove them unless DRY_RUN.

    Returns a list of detected oversized file paths. If DRY_RUN is False the files will be removed.
    """
    logger.info("[CLEAN] Scanning %s for files > %s MB", REPO_PATH, threshold)
    oversized = []
    for root, _, files in os.walk(REPO_PATH):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                if os.path.isfile(full_path):
                    size_mb = file_size_mb(full_path)
                    if size_mb > threshold:
                        oversized.append((full_path, size_mb))
            except Exception:
                # ignore files we cannot stat
                continue

    if not oversized:
        logger.info("No oversized files found.")
        return []
    logger.warning("Oversized files:")
    for path, size in oversized:
        logger.warning(" - %s (%.2f MB)", path, size)

    if DRY_RUN:
        logger.info("DRY_RUN enabled: not removing files")
        return [p for p, _ in oversized]
    removed = []
    for path, _ in oversized:
        try:
            os.remove(path)
            removed.append(path)
            logger.info("Removed: %s", path)
        except Exception as e:
            logger.exception("Failed to remove %s: %s", path, e)

    return removed


def file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)


def detect_oversized_files():
    logger.info(
        "Checking for oversized files in %s with threshold %s MB",
        REPO_PATH,
        MAX_FILE_SIZE_MB,
    )

    oversized = []
    for root, _, files in os.walk(REPO_PATH):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                if (
                    os.path.isfile(full_path)
                    and file_size_mb(full_path) > MAX_FILE_SIZE_MB
                ):
                    oversized.append((full_path, file_size_mb(full_path)))
            except Exception:
                continue

    if oversized:
        logger.warning("Oversized files detected:")
        for path, size in oversized:
            logger.warning(" - %s (%.2f MB)", path, size)
        if not DRY_RUN:
            raise Exception("Oversized files must be removed or git-lfs configured.")
    else:
        logger.info("No oversized files found.")
