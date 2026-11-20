"""Walk-forward backtest of the systematic pipeline. Analysts' views cannot be backtested;
say so in every output header."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 6 (M7): write the walk-forward backtest"

Engine = Callable[[Panel, pd.Timestamp], pd.Series]


def walk_forward(
    cfg: Config,
    start: str | None = None,
    engine: Engine | None = None,
    panel: Panel | None = None,
) -> pd.DataFrame:
    """For each month-end from `start`: weights = engine(panel, as_of); hold one month; charge
    risk.cost_bp_one_way on turnover. Assert inside the loop that nothing after as_of is read.

    Returns one row per month: weights_date, active_return (after costs), turnover, cost."""
    raise NotImplementedError(TODO)


def performance_stats(active_returns: pd.Series) -> dict[str, float]:
    """Annualized active return, realized TE, IR with Newey-West t, hit rate, max relative DD."""
    raise NotImplementedError(TODO)
