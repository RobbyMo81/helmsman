from chardet import detect
import logging

logger = logging.getLogger(__name__)


def run_encoding_audit(paths, dry_run=True):
    results = []
    for path in paths:
        try:
            with open(path, "rb") as f:
                raw = f.read()
            encoding = detect(raw)["encoding"]
            newline_ok = raw.endswith(b"\n")
            results.append((path, encoding, newline_ok))
        except Exception as e:
            results.append((path, "Unreadable", False))

    for path, encoding, newline_ok in results:
        enc_lower = (encoding or "").lower()
        status = "✅" if enc_lower == "utf-8" and newline_ok else "⚠️"
        logger.info(
            "%s %s — Encoding: %s, Newline: %s", status, path, encoding, newline_ok
        )

    if dry_run:
        logger.info("🧪 Dry-run complete. No files modified.")
