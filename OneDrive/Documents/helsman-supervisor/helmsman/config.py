from __future__ import annotations
import os, pathlib, yaml
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

HOME = pathlib.Path.home()
XDG = pathlib.Path(os.environ.get("XDG_CONFIG_HOME", HOME/".config"))
APP = "helmsman"

DEFAULT_CFG: Dict[str, Any] = {
    "python": "python",
    "requirements": "requirements.txt",
    "streamlit": {
        "entry": "apps/data_analyzer_streamlit/app.py",
        "port": 8501,
        "args": ["--server.headless", "true", "--server.address", "127.0.0.1"],
    },
    "torch_app": {
        "entry": "apps/analyzer_torch/main.py",
        "default_device": "cuda",
        "infile": None,
    },
    "pytest": {"enabled": True, "args": ["-q"]},
}

@dataclass
class Config:
    root: pathlib.Path
    data: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CFG.copy())

    @staticmethod
    def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge dict b into dict a and return a new dict.

        Values from b take precedence. This does not mutate the inputs.
        """
        out: Dict[str, Any] = {}
        for key in set(a) | set(b):
            if key in a and key in b:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    out[key] = Config._deep_merge(a[key], b[key])
                else:
                    out[key] = b[key]
            elif key in b:
                out[key] = b[key]
            else:
                out[key] = a[key]
        return out

    @staticmethod
    def discover(explicit: Optional[str] = None) -> "Config":
        # precedence: CLI --config > .helmsman.yaml > supervisor.yaml > ~/.config/helmsman/config.yaml > defaults
        candidates = []
        if explicit:
            candidates.append(pathlib.Path(explicit))
        cwd = pathlib.Path.cwd()
        candidates += [cwd/".helmsman.yaml", cwd/"supervisor.yaml", XDG/APP/"config.yaml"]
        for c in candidates:
            if c and c.exists():
                with open(c, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
                    merged = Config._deep_merge(DEFAULT_CFG, loaded)
                    return Config(root=cwd, data=merged)
        return Config(root=cwd)

    def validate(self) -> None:
        """Validate `self.data`. Raises ValueError with a newline-separated list of problems if invalid."""
        errors = []
        # streamlit
        st = self.data.get("streamlit")
        if not isinstance(st, dict):
            errors.append("'streamlit' must be a mapping")
        else:
            entry = st.get("entry")
            if not entry:
                errors.append("streamlit.entry is required")
            port = st.get("port")
            try:
                if port is None:
                    errors.append("streamlit.port is required")
                else:
                    int(port)
            except Exception:
                errors.append("streamlit.port must be an integer")

        # torch_app
        ta = self.data.get("torch_app")
        if not isinstance(ta, dict):
            errors.append("'torch_app' must be a mapping")
        else:
            if not ta.get("entry"):
                errors.append("torch_app.entry is required")

        # requirements
        req = self.data.get("requirements")
        if req is not None and not isinstance(req, (str, pathlib.Path)):
            errors.append("requirements must be a path string if provided")

        if errors:
            raise ValueError("\n".join(errors))

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def write_default(self, path: Optional[pathlib.Path] = None):
        tgt = path or (self.root/".helmsman.yaml")
        tgt.parent.mkdir(parents=True, exist_ok=True)
        with open(tgt, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.data, f, sort_keys=False)

    def asdict(self):
        return self.data
