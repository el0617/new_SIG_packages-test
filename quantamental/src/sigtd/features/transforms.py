"""Series transforms. Every z-score uses only past data (rolling or expanding)."""

from __future__ import annotations

import pandas as pd

TODO = "Phase 1 (M1): write transforms"


def yoy(s: pd.Series) -> pd.Series:
    """12-month percent change."""
    raise NotImplementedError(TODO)


def ann3m(s: pd.Series) -> pd.Series:
    """3-month change, annualized, in percent: ((s / s.shift(3)) ** 4 - 1) * 100."""
    raise NotImplementedError(TODO)


def ann6m(s: pd.Series) -> pd.Series:
    """6-month change, annualized, in percent."""
    raise NotImplementedError(TODO)


def zscore_rolling(s: pd.Series, window: int, min_periods: int) -> pd.Series:
    raise NotImplementedError(TODO)


def zscore_expanding(s: pd.Series, min_periods: int) -> pd.Series:
    raise NotImplementedError(TODO)


def apply_transform(s: pd.Series, name: str) -> pd.Series:
    """Dispatch on the registry's transform name (level, yoy, yoy_inv, ann3m, ann6m, diff)."""
    raise NotImplementedError(TODO)
