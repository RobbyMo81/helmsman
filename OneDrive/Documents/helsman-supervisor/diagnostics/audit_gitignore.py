import chardet
import logging

logger = logging.getLogger(__name__)


def audit_gitignore(path=".gitignore", dry_run=True):
    try:
        with open(path, "rb") as f:
            raw = f.read()
        encoding = chardet.detect(raw)["encoding"]
        newline_ok = raw.endswith(b"\n")

        if dry_run:
            logger.info("[DRY-RUN] .gitignore encoding: %s", encoding)
            logger.info("[DRY-RUN] Ends with newline: %s", newline_ok)
        else:
            # chardet.detect may return None for 'encoding' if it cannot determine it
            if not encoding:
                raise ValueError(".gitignore encoding could not be detected")
            if encoding.lower() != "utf-8":
                raise ValueError(f".gitignore is not UTF-8 (found {encoding})")
            if not newline_ok:
                raise ValueError(".gitignore missing final newline")
        return True
    except Exception as e:
        logger.exception("[ERROR] %s", e)
        return False
