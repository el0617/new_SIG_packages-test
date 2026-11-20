"""Forecast-light construction: spend a tracking-error budget on insurance, sized by recession risk.

In the quantamental repo this is the fallback ('risk-budget mode') when no view is confident.
"""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 5 (M6): write the risk-budget engine"


def te_target(p_recession: float, cfg: Config) -> float:
    """Linear in p between insurance.p_low and p_high, from te_min to te_max, clipped."""
    raise NotImplementedError(TODO)


def scale_to_te(active: pd.Series, cov: pd.DataFrame, target: float) -> pd.Series:
    """Scale a self-funding active vector so its annualized tracking error equals `target`."""
    raise NotImplementedError(TODO)


def propose(panel: Panel, as_of: pd.Timestamp, cfg: Config, p_recession: float) -> pd.Series:
    """Benchmark + scaled insurance, then enforce mandate limits. Returns weights summing to 1."""
    raise NotImplementedError(TODO)
