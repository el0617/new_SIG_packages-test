"""Command line entry points used by the Makefile.

python -m sigtd.cli data                      # rebuild every cache from scratch
python -m sigtd.cli dashboard [--as-of DATE]
python -m sigtd.cli weekly [--as-of DATE]     # the Friday brief
python -m sigtd.cli backtest [--start DATE]
"""

from __future__ import annotations

import argparse

import pandas as pd

from sigtd.config import load_config


def _as_of(value: str | None) -> pd.Timestamp:
    """Run date (default today). Publication timing is resolved inside Panel.as_of."""
    return pd.Timestamp(value) if value else pd.Timestamp.today().normalize()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="sigtd")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("data")
    for name in ("dashboard", "weekly"):
        sub.add_parser(name).add_argument("--as-of")
    sub.add_parser("backtest").add_argument("--start")
    args = parser.parse_args(argv)
    cfg = load_config()

    if args.cmd == "data":
        from sigtd.data.panel import build_panel

        build_panel(cfg, refresh=True)
    elif args.cmd == "dashboard":
        from sigtd.data.panel import build_panel
        from sigtd.report.dashboard import render_dashboard

        render_dashboard(build_panel(cfg), _as_of(args.as_of), cfg)
    elif args.cmd == "weekly":
        from sigtd.pipeline import run_weekly

        run_weekly(cfg, _as_of(args.as_of))
    elif args.cmd == "backtest":
        from sigtd.risk.backtest import walk_forward

        walk_forward(cfg, start=args.start or cfg.get("backtest.start"))


if __name__ == "__main__":
    main()
