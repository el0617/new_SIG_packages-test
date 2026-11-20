"""Command line entry points used by the Makefile.

python -m sigtd.cli data                      # download every series (FRED key + network)
python -m sigtd.cli dashboard [--as-of DATE]
python -m sigtd.cli research                  # signal scorecard -> outputs/ (frozen)
python -m sigtd.cli backtest [--start DATE]   # three systematic engines -> outputs/
python -m sigtd.cli weekly [--as-of DATE] [--views PATH|none]
python -m sigtd.cli demo                      # research + backtest + both brief modes
"""

from __future__ import annotations

import argparse
import warnings

import pandas as pd

from sigtd.config import load_config


def _as_of(value: str | None) -> pd.Timestamp:
    """Run date (default today). Publication timing is resolved inside Panel.as_of."""
    return pd.Timestamp(value) if value else pd.Timestamp.today().normalize()


def research(cfg) -> None:
    from sigtd.data.panel import build_panel
    from sigtd.pipeline import OUTPUTS, SCORECARD
    from sigtd.signals.evaluate import scorecard

    card, ics = scorecard(build_panel(cfg), cfg)
    OUTPUTS.mkdir(exist_ok=True)
    card.to_csv(SCORECARD)
    ics.to_csv(OUTPUTS / "signal_ic_history.csv")
    cols = ["status", "mean_ic", "t_stat", "power_threshold_ic", "verdict", "confidence"]
    print(card.reindex(columns=cols).round(3).to_string())


def backtest(cfg, start: str | None) -> None:
    from sigtd.data.panel import build_panel
    from sigtd.pipeline import OUTPUTS
    from sigtd.risk.backtest import (
        benchmark_engine,
        performance_stats,
        risk_budget_engine,
        signals_bl_engine,
        walk_forward,
    )

    panel = build_panel(cfg)
    engines = {
        "signals + Black-Litterman": signals_bl_engine(cfg),
        "risk-budget fallback": risk_budget_engine(cfg),
        "benchmark": benchmark_engine,
    }
    active, summary = {}, {}
    for name, engine in engines.items():
        print(f"backtesting {name} ...", flush=True)
        res = walk_forward(cfg, start=start, engine=engine, panel=panel)
        active[name] = res["active_return"]
        summary[name] = {
            **performance_stats(res["active_return"]),
            "avg_turnover_pct": res["turnover"].mean() * 100,
        }
    OUTPUTS.mkdir(exist_ok=True)
    pd.DataFrame(active).to_csv(OUTPUTS / "backtest_active.csv")
    table = pd.DataFrame(summary).T
    table.to_csv(OUTPUTS / "backtest_summary.csv")
    print(table.round(2).to_string())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="sigtd")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("data")
    sub.add_parser("dashboard").add_argument("--as-of")
    weekly = sub.add_parser("weekly")
    weekly.add_argument("--as-of")
    weekly.add_argument("--views", help="path to a view sheet, or 'none' (default: real or demo)")
    sub.add_parser("backtest").add_argument("--start")
    sub.add_parser("research")
    sub.add_parser("demo")
    args = parser.parse_args(argv)
    cfg = load_config()
    warnings.filterwarnings("ignore", category=FutureWarning)

    if args.cmd == "data":
        from sigtd.data.panel import build_panel

        build_panel(cfg, refresh=True)
    elif args.cmd == "dashboard":
        from sigtd.data.panel import build_panel
        from sigtd.report.dashboard import render_dashboard

        print(render_dashboard(build_panel(cfg), _as_of(args.as_of), cfg))
    elif args.cmd == "research":
        research(cfg)
    elif args.cmd == "backtest":
        backtest(cfg, args.start)
    elif args.cmd == "weekly":
        from sigtd.pipeline import run_weekly

        print(run_weekly(cfg, _as_of(args.as_of), views=args.views))
    elif args.cmd == "demo":
        from sigtd.data.panel import build_panel
        from sigtd.pipeline import run_weekly
        from sigtd.report.dashboard import render_dashboard

        research(cfg)
        backtest(cfg, None)
        panel = build_panel(cfg)
        as_of = _as_of(None)
        print(render_dashboard(panel, as_of, cfg))
        print(run_weekly(cfg, as_of, views=None, panel=panel))
        print(run_weekly(cfg, as_of, views="none", panel=panel))


if __name__ == "__main__":
    main()
