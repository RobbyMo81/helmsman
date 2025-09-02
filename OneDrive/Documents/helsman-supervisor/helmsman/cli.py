from __future__ import annotations
import sys
from rich.console import Console
from rich.table import Table
from .config import Config
from .runtime import bootstrap, health as do_health, run_streamlit, run_torch, status
from .process import stop, stop_all
from .report import build_report

console = Console()

def _print_health(h):
    t = Table(title="Helmsman Health", show_lines=True)
    t.add_column("Metric"); t.add_column("Value")
    t.add_row("Python", h.python)
    t.add_row("Venv Exists", str(h.has_venv))
    t.add_row("Torch OK", str(h.torch_ok))
    t.add_row("CUDA Available", str(h.cuda_available))
    t.add_row("Reqs OK", str(h.requirements_ok))
    for k, v in h.ports_free.items(): t.add_row(f"Port free: {k}", str(v))
    if h.notes: t.add_row("Notes", " | ".join(h.notes))
    console.print(t)

USAGE = """
Helmsman – single-host supervisor

Usage:
  helmsman init-config                   # write a default .helmsman.yaml in CWD
  helmsman bootstrap [--config PATH]
  helmsman health [--config PATH]
  helmsman test [--config PATH]         # (reserved) – call pytest if you add it later
  helmsman run streamlit [--config PATH]
  helmsman run torch [--config PATH] [--infile P] [--device cpu|cuda] [--max-batch N]
  helmsman status
  helmsman stop [name|all]
  helmsman report
"""

def main(argv=None):
    import argparse

    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(prog="helmsman", add_help=False)
    parser.add_argument("command", nargs="*")
    parser.add_argument("--config", dest="config", help="Path to config YAML", default=None)
    args, unknown = parser.parse_known_args(argv)

    if not args.command:
        console.print(USAGE); return 0

    cfg = Config.discover(args.config)
    try:
        cfg.validate()
    except Exception as e:
        console.print(f"Config validation failed:\n{e}")
        return 2
    cmd = args.command[0]

    if cmd == "init-config":
        cfg.write_default(); console.print("Wrote .helmsman.yaml"); return 0

    if cmd == "bootstrap":
        return bootstrap(cfg.asdict())

    if cmd == "health":
        h = do_health(cfg.asdict()); _print_health(h); return 0

    if cmd == "run":
        if len(args.command) < 2:
            console.print(USAGE); return 2
        which = args.command[1]
        # parse run-specific flags from unknown
        from argparse import ArgumentParser
        runp = ArgumentParser(prog="helmsman run")
        runp.add_argument("target", choices=["streamlit", "torch"])
        runp.add_argument("--infile", default=None)
        runp.add_argument("--device", default=cfg.data.get("torch_app", {}).get("default_device"))
        runp.add_argument("--max-batch", type=int, default=8)
        rargs = runp.parse_args(args.command[1:] + unknown)

        if rargs.target == "streamlit":
            run_streamlit(cfg.asdict()); console.print("Launched Streamlit (see artifacts/logs/streamlit.log)"); return 0
        elif rargs.target == "torch":
            run_torch(cfg.asdict(), rargs.infile, rargs.device, rargs.max_batch)
            console.print("Launched Torch (see artifacts/logs/torch.log)")
            return 0

    if cmd == "status":
        t = Table(title="Running Processes"); t.add_column("Name"); t.add_column("PID"); t.add_column("Log")
        for p in status(): t.add_row(p.name, str(p.pid), p.log_file)
        console.print(t); return 0

    if cmd == "stop":
        target = args.command[1] if len(args.command) > 1 else "all"
        if target == "all":
            for msg in stop_all(): console.print(msg)
        else:
            console.print(stop(target))
        return 0

    if cmd == "report":
        path = build_report(); console.print(f"Wrote: {path}\nMarkdown: artifacts/reports/supervision_report.md"); return 0

    console.print(USAGE); return 2
