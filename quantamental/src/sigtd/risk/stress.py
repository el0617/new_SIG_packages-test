"""Stress tests: replay history on today's weights, and shock it through M3 betas."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 6 (M7): write stress tests"


def historical_replays(
    weights: pd.Series, panel: Panel, as_of: pd.Timestamp, cfg: Config
) -> pd.DataFrame:
    """Active return of today's weights over each risk.historical_windows window."""
    raise NotImplementedError(TODO)


def factor_shocks(weights: pd.Series, benchmark: pd.Series, betas: pd.DataFrame) -> pd.DataFrame:
    """Active return under 10y +100bp, oil +30%, credit +200bp, growth -1 sd, via M3 betas."""
    raise NotImplementedError(TODO)
