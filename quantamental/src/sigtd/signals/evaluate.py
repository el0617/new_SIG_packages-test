"""Walk-forward evaluation: rank IC, Newey-West t, tercile spreads, turnover, scorecard."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 3 (M4): write the evaluation engine"


def rank_ic(scores: pd.DataFrame, next_returns: pd.DataFrame) -> pd.Series:
    """Monthly Spearman correlation across sectors between scores at t (row t) and returns
    over t+1 (also row t: align before calling)."""
    raise NotImplementedError(TODO)


def ic_summary(ic: pd.Series, nw_lags: int = 1) -> dict[str, float]:
    """mean_ic, t_stat (Newey-West), ic_ir, hit_rate, n_months."""
    raise NotImplementedError(TODO)


def tercile_spread(scores: pd.DataFrame, next_returns: pd.DataFrame) -> pd.Series:
    raise NotImplementedError(TODO)


def turnover(scores: pd.DataFrame) -> float:
    raise NotImplementedError(TODO)


def scorecard(panel: Panel, cfg: Config) -> pd.DataFrame:
    """One row per pre-registered signal plus the equal-weight composite: IC stats, power
    threshold, Holm-adjusted verdict (oos_value / weak / none) and the mapped confidence."""
    raise NotImplementedError(TODO)
