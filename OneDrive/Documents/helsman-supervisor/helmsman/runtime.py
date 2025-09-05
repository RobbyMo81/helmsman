from __future__ import annotations
import os, sys, json, time, socket, subprocess, pathlib
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

VENV = "venv"
ART = pathlib.Path("artifacts")
LOG = ART / "logs"
REP = ART / "reports"


@dataclass
class Health:
    timestamp: float
    python: str
    has_venv: bool
    torch_ok: bool
    cuda_available: Optional[bool]
    requirements_ok: Optional[bool]
    ports_free: Dict[str, bool]
    notes: List[str]


@dataclass
class ProcInfo:
    name: str
    pid: int
    cmd: List[str]
    log_file: str
    start_time: float
    # store the Popen object and the open log file handle so we can terminate/cleanup reliably
    proc: Optional[subprocess.Popen] = None
    log_handle: Optional[Any] = None


PROCS: Dict[str, ProcInfo] = {}


def ensure_dirs():
    for d in [ART, LOG, REP]:
        d.mkdir(parents=True, exist_ok=True)


def port_is_free(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def write_json(path: pathlib.Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------- bootstrap ----------------


def bootstrap(cfg: Dict[str, Any]) -> int:
    ensure_dirs()
    venv = pathlib.Path(VENV)
    if not venv.exists():
        rc = subprocess.call([sys.executable, "-m", "venv", str(venv)])
        if rc != 0:
            return rc
    req = cfg.get("requirements")
    if req and pathlib.Path(req).exists():
        pip = str(venv / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip"))
        rc = subprocess.call([pip, "install", "-r", req])
        if rc != 0:
            return rc
    return 0


# ---------------- health -------------------


def health(cfg: Dict[str, Any]) -> Health:
    ensure_dirs()
    notes: List[str] = []
    has_venv = pathlib.Path(VENV).exists()
    torch_ok, cuda = False, None
    try:
        import importlib

        torch = importlib.import_module("torch")
        torch_ok = True
        cuda = bool(getattr(torch, "cuda", None) and torch.cuda.is_available())
    except Exception as e:
        notes.append(f"torch import failed: {e}")
    requirements_ok = bool(
        cfg.get("requirements") and pathlib.Path(cfg["requirements"]).exists()
    )
    ports = {"streamlit": port_is_free(int(cfg["streamlit"]["port"]))}
    h = Health(
        time.time(),
        sys.version.split(" ")[0],
        has_venv,
        torch_ok,
        cuda,
        requirements_ok,
        ports,
        notes,
    )
    write_json(REP / "health.json", asdict(h))
    return h


# ---------------- process mgmt ------------


def _py() -> str:
    venv = pathlib.Path(VENV)
    return str(venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))


def _launch(name: str, cmd: List[str], log_path: pathlib.Path) -> Optional[ProcInfo]:
    ensure_dirs()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_f = open(log_path, "a", buffering=1, encoding="utf-8")
    p = subprocess.Popen(
        cmd, stdout=log_f, stderr=subprocess.STDOUT, cwd=str(pathlib.Path.cwd())
    )
    info = ProcInfo(
        name=name,
        pid=p.pid,
        cmd=cmd,
        log_file=str(log_path),
        start_time=time.time(),
        proc=p,
        log_handle=log_f,
    )
    PROCS[name] = info
    return info


def run_streamlit(cfg: Dict[str, Any]):
    entry = pathlib.Path(cfg["streamlit"]["entry"])
    port = str(cfg["streamlit"]["port"])
    if not entry.exists():
        raise FileNotFoundError(f"No Streamlit entry: {entry}")
    if not port_is_free(int(port)):
        raise RuntimeError(f"Port {port} not free")
    args = cfg["streamlit"].get("args", [])
    cmd = [_py(), "-m", "streamlit", "run", str(entry), "--server.port", port, *args]
    return _launch("streamlit", cmd, LOG / "streamlit.log")


def run_torch(
    cfg: Dict[str, Any], infile: Optional[str], device: Optional[str], max_batch: int
):
    entry = pathlib.Path(cfg["torch_app"]["entry"])
    if not entry.exists():
        raise FileNotFoundError(f"No Torch entry: {entry}")
    cmd = [_py(), str(entry)]
    if infile:
        cmd += ["--infile", infile]
    if device:
        cmd += ["--device", device]
    if max_batch:
        cmd += ["--max-batch", str(max_batch)]
    return _launch("torch", cmd, LOG / "torch.log")


def status() -> List[ProcInfo]:
    return list(PROCS.values())
