"""Recession probability 12 months ahead (Estrella-Mishkin lineage), estimated out of sample."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 4 (M5): write the recession model (pre-register in docs/prereg first)"


def make_target(usrec: pd.Series, horizon: int = 12) -> pd.Series:
    """y_t = 1 if any month in t+1..t+horizon is a recession month; NaN where unknown."""
    raise NotImplementedError(TODO)


def training_window(target: pd.Series, as_of: pd.Timestamp, embargo_months: int) -> pd.Series:
    """Labels usable at as_of: drop the last `embargo_months` (NBER dates recessions late)."""
    raise NotImplementedError(TODO)


def features(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """10y-3m spread, credit spread, 26-week change in 4-week-average claims, month-end, lagged."""
    raise NotImplementedError(TODO)


def recession_probability(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> float:
    """Fit the logit on the expanding, embargoed window and predict for as_of."""
    raise NotImplementedError(TODO)


def out_of_sample_path(panel: Panel, cfg: Config, start: str) -> pd.Series:
    """recession_probability for every month from `start`: the series you score and plot."""
    raise NotImplementedError(TODO)
