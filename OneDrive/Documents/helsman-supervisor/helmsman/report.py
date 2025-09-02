from __future__ import annotations
import time, json, pathlib
from typing import List, Dict, Any
from .runtime import LOG, REP, write_json, status

def _tail(p: pathlib.Path, n: int = 200) -> List[str]:
    if not p.exists(): return []
    try: return p.read_text(encoding="utf-8", errors="ignore").splitlines()[-n:]
    except Exception: return []

def build_report() -> pathlib.Path:
    try: health = json.loads((REP/"health.json").read_text())
    except Exception: health = {}
    # serialize proc info safely: avoid including Popen or open file handles
    procs = []
    for p in status():
        safe = {"name": p.name, "pid": p.pid, "cmd": p.cmd, "log_file": p.log_file, "start_time": p.start_time}
        procs.append(safe)
    summary: Dict[str, Any] = {
        "generated_at": time.time(),
        "health": health,
        "procs": procs,
        "logs": {
            "streamlit_tail": _tail(LOG/"streamlit.log"),
            "torch_tail": _tail(LOG/"torch.log"),
            "pytest_tail": _tail(LOG/"pytest.log"),
        },
    }
    out = REP / f"supervision_report_{int(time.time())}.json"
    write_json(out, summary)
    (REP/"supervision_report.md").write_text(
        "# Helmsman Supervision Report\n\n"
        + f"Generated: {time.ctime(summary['generated_at'])}\n\n"
        + "## Health\n\n"
        + json.dumps(summary.get("health", {}), indent=2) + "\n\n"
        + "## Processes\n\n"
        + json.dumps(summary.get("procs", []), indent=2) + "\n\n"
        + "## Log tails\n\n### Streamlit\n\n"
        + "\n".join(summary["logs"]["streamlit_tail"]) + "\n\n"
        + "### Torch\n\n"
        + "\n".join(summary["logs"]["torch_tail"]) + "\n\n"
        + "### Pytest\n\n"
        + "\n".join(summary["logs"]["pytest_tail"]) + "\n",
        encoding="utf-8",
    )
    return out
