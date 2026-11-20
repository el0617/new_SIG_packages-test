"""Series transforms. Every z-score uses only past data (rolling or expanding)."""

from __future__ import annotations

import pandas as pd


def yoy(s: pd.Series) -> pd.Series:
    """12-month percent change."""
    return (s / s.shift(12) - 1) * 100


def ann3m(s: pd.Series) -> pd.Series:
    """3-month change, annualized, in percent."""
    return ((s / s.shift(3)) ** 4 - 1) * 100


def ann6m(s: pd.Series) -> pd.Series:
    """6-month change, annualized, in percent."""
    return ((s / s.shift(6)) ** 2 - 1) * 100


def diff(s: pd.Series, n: int = 1) -> pd.Series:
    return s - s.shift(n)


def zscore_rolling(s: pd.Series, window: int, min_periods: int) -> pd.Series:
    r = s.rolling(window, min_periods=min_periods)
    return (s - r.mean()) / r.std()


def zscore_expanding(s: pd.Series, min_periods: int) -> pd.Series:
    r = s.expanding(min_periods=min_periods)
    return (s - r.mean()) / r.std()


def zscore(s: pd.Series, window: int | str, min_periods: int) -> pd.Series:
    """window = an integer number of months, or "expanding"."""
    if window == "expanding":
        return zscore_expanding(s, min_periods)
    return zscore_rolling(s, int(window), min_periods)


def apply_transform(s: pd.Series, name: str) -> pd.Series:
    """Dispatch on the registry's transform name."""
    funcs = {
        "level": lambda x: x,
        "yoy": yoy,
        "yoy_inv": lambda x: -yoy(x),
        "ann3m": ann3m,
        "ann6m": ann6m,
        "diff": diff,
    }
    if name not in funcs:
        raise ValueError(f"unknown transform {name!r}")
    return funcs[name](s)
