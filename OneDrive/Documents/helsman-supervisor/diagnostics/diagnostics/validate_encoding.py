import chardet
import subprocess
import logging

logger = logging.getLogger(__name__)


def get_tracked_files():
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    return result.stdout.strip().split("\n")


def validate_utf8():
    bad_files = []
    for f in get_tracked_files():
        try:
            with open(f, "rb") as file:
                raw = file.read()
            detected = chardet.detect(raw)
            encoding = detected.get("encoding")
            if not encoding:
                bad_files.append((f, "Unknown"))
            elif encoding.lower() != "utf-8":
                bad_files.append((f, encoding))
        except Exception:
            bad_files.append((f, "Unreadable"))
    if bad_files:
        logger.error("[FAIL] Non-UTF-8 files detected:")
        for f, enc in bad_files:
            logger.error(" - %s: %s", f, enc)
        exit(1)
    else:
        logger.info("[PASS] All files are UTF-8 encoded.")


if __name__ == "__main__":
    validate_utf8()
