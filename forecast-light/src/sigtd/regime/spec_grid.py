"""Run the classifier over a grid of reasonable specifications; report agreement, not one label."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 2 (M2): write the spec grid"


def spec_grid(cfg: Config) -> list[dict]:
    """Cartesian product of regime.grid in config (expect 9-12 specs)."""
    raise NotImplementedError(TODO)


def regime_shares(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Share of specs placing `as_of` in each regime (index = REGIMES, sums to 1)."""
    raise NotImplementedError(TODO)


def real_time_vs_revised(panel: Panel, cfg: Config) -> pd.DataFrame:
    """Labels from vintage data vs today's revised data, month by month. Your look-ahead exhibit."""
    raise NotImplementedError(TODO)
