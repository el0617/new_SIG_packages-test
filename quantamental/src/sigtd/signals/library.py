"""Pre-registered signals. Each returns an 11-sector score vector for any as_of,
z-scored across sectors that month. Do not add signals after seeing results."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 3 (M4): write the signal library (pre-register in docs/prereg first)"

Signal = Callable[[Panel, pd.Timestamp, Config], pd.Series]


def momentum_12_1(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Cumulative excess return t-12..t-1, skipping the latest month (Moskowitz-Grinblatt)."""
    raise NotImplementedError(TODO)


def revision_breadth(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """(up - down) / total forward-EPS revisions, 3-month average (Bloomberg)."""
    raise NotImplementedError(TODO)


def relative_valuation(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Minus z-score of forward P/E relative to the market, vs its own trailing 10 years."""
    raise NotImplementedError(TODO)


def regime_conditional(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Average excess return in the current regime mix (M2 shares), estimated on data before
    as_of only, shrunk toward zero."""
    raise NotImplementedError(TODO)


def macro_tilt(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """M3 rolling growth beta x latest 3-month change of the growth composite."""
    raise NotImplementedError(TODO)


SIGNALS: dict[str, Signal] = {
    "momentum_12_1": momentum_12_1,
    "revision_breadth": revision_breadth,
    "relative_valuation": relative_valuation,
    "regime_conditional": regime_conditional,
    "macro_tilt": macro_tilt,
}
