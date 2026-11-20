"""Growth and inflation composites and the quadrant classifier (Investment Clock lineage)."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 2 (M2): write the regime classifier (pre-register in docs/prereg first)"

# growth sign, inflation sign -> label; inside the neutral band -> Transition
REGIMES = ("Goldilocks", "Reflation", "Stagflation", "Slowdown", "Transition")


def growth_composite(panel: Panel, as_of: pd.Timestamp, cfg: Config, **spec) -> pd.Series:
    """Average z-score of the growth block (payrolls, IP, real retail sales, inverted claims,
    survey new orders), with a minimum-components rule."""
    raise NotImplementedError(TODO)


def inflation_composite(panel: Panel, as_of: pd.Timestamp, cfg: Config, **spec) -> pd.Series:
    """6-month annualized core CPI and core PCE against their anchors, merged into one block."""
    raise NotImplementedError(TODO)


def classify(growth: pd.Series, inflation: pd.Series, band: float, sticky: bool) -> pd.Series:
    """Label each month. |composite| < band on either axis -> Transition, unless sticky and the
    previous label is still consistent with the signs (hysteresis)."""
    raise NotImplementedError(TODO)
