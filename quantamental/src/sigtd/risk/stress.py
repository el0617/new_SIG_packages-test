"""Stress tests: replay history on today's weights, and shock them through M3 betas."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel


def historical_replays(
    weights: pd.Series, panel: Panel, as_of: pd.Timestamp, cfg: Config
) -> pd.DataFrame:
    """Portfolio, benchmark and active return of today's weights over each historical window."""
    b = panel.benchmark(as_of)
    r = panel.returns_through(as_of)
    rows = []
    for name, (start, end) in dict(cfg.get("risk.historical_windows")).items():
        window = r.loc[start:end].fillna(0.0)
        if window.empty:
            continue
        port = np.prod(1 + window @ weights.values) - 1
        bench = np.prod(1 + window @ b.values) - 1
        rows.append(
            {
                "scenario": name,
                "months": len(window),
                "portfolio_pct": port * 100,
                "benchmark_pct": bench * 100,
                "active_pct": (port - bench) * 100,
            }
        )
    return pd.DataFrame(rows)


def factor_shocks(
    weights: pd.Series,
    benchmark: pd.Series,
    beta_matrix: pd.DataFrame,
    cfg: Config,
    factor_sd: pd.Series | None = None,
) -> pd.DataFrame:
    """Active return under each configured factor shock, via relative-return betas.

    Shocks on 'growth' are in standard deviations of its monthly change (pass factor_sd).
    """
    a = (weights - benchmark).reindex(beta_matrix.index).fillna(0.0)
    rows = []
    for name, shock in dict(cfg.get("risk.factor_shocks")).items():
        move = pd.Series(0.0, index=beta_matrix.columns)
        for f, size in dict(shock).items():
            scale = factor_sd[f] if (f == "growth" and factor_sd is not None) else 1.0
            move[f] = size * scale
        sector_rel = beta_matrix @ move
        rows.append({"shock": name, "active_pct": float(a @ sector_rel) * 100})
    return pd.DataFrame(rows)
