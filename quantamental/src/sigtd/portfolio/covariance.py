"""Covariance of monthly sector excess returns."""

from __future__ import annotations

import pandas as pd

from sigtd.data.panel import Panel

TODO = "Phase 5 (M6): write covariance estimators"


def ledoit_wolf(panel: Panel, as_of: pd.Timestamp, months: int = 60) -> pd.DataFrame:
    """Shrunk covariance of the last `months` of monthly returns up to as_of (monthly units)."""
    raise NotImplementedError(TODO)


def ewma(panel: Panel, as_of: pd.Timestamp, halflife_months: int = 24) -> pd.DataFrame:
    raise NotImplementedError(TODO)
