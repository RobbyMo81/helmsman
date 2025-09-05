from __future__ import annotations
import time
from typing import List
from .runtime import PROCS


def stop(name: str):
    pinfo = PROCS.get(name)
    if not pinfo:
        return f"{name} not running"
    # try graceful termination via Popen if available
    proc = getattr(pinfo, "proc", None)
    if proc:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    else:
        # fallback: best-effort using os.kill by pid (not ideal)
        try:
            import os, signal

            os.kill(pinfo.pid, signal.SIGTERM)
        except Exception:
            pass

    # close log handle if present
    try:
        lh = getattr(pinfo, "log_handle", None)
        if lh:
            try:
                lh.close()
            except Exception:
                pass
    except Exception:
        pass

    PROCS.pop(name, None)
    return f"Stopped {name}"


def stop_all() -> List[str]:
    names = list(PROCS.keys())
    msgs: List[str] = []
    for n in names:
        msgs.append(stop(n))
    return msgs
