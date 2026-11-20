"""Analog regimes (Mulliner, Harvey et al., 'Regimes', JPM 2026): find past months whose
economic state looks most like today's, without presupposing regime definitions."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 2 (M2 cross-check): write similarity regimes"


def state_matrix(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """Annual changes of similarity.variables, z-scored on data up to as_of."""
    raise NotImplementedError(TODO)


def similar_periods(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DatetimeIndex:
    """Months in the most-similar quantile by summed squared z-score distance (exclude the
    last 36 months so today's own neighbourhood does not dominate)."""
    raise NotImplementedError(TODO)
