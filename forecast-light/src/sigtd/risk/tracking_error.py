"""Ex-ante tracking error and its Euler split (annualized from monthly covariance)."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 6 (M7): write tracking error"


def tracking_error(active: pd.Series, cov: pd.DataFrame) -> float:
    """sqrt(12 a' Sigma a)."""
    raise NotImplementedError(TODO)


def mctr(active: pd.Series, cov: pd.DataFrame) -> pd.Series:
    """12 (Sigma a)_i / TE."""
    raise NotImplementedError(TODO)


def contributions(active: pd.Series, cov: pd.DataFrame) -> pd.Series:
    """a_i * MCTR_i; sums to TE."""
    raise NotImplementedError(TODO)


def risk_report(weights: pd.Series, panel: Panel, as_of: pd.Timestamp, cfg: Config) -> dict:
    """TE, beta to SPY, contributions, VaR/CVaR, limit checks."""
    raise NotImplementedError(TODO)
