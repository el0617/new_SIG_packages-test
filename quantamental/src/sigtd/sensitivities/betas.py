"""Sector excess returns regressed on macro factor changes, with HAC errors."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 2 (M3): write sector betas"


def factor_changes(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """Monthly changes of sensitivities.factors, point-in-time."""
    raise NotImplementedError(TODO)


def sector_betas(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """Sectors x factors: beta, HAC t-stat, VIF. Full sample up to as_of."""
    raise NotImplementedError(TODO)


def rolling_betas(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """36-month rolling betas (long format: date, sector, factor, beta)."""
    raise NotImplementedError(TODO)


def split_sample_flags(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """True where a beta changes sign between the first and second half of the sample."""
    raise NotImplementedError(TODO)
