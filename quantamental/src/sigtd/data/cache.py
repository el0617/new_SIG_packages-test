"""Read the CSV cache (FRED download format: a date column and one value column)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_fred_csv(path: Path) -> pd.Series:
    df = pd.read_csv(path, index_col=0)
    s = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    s.index = pd.to_datetime(df.index)
    s = s.dropna().sort_index()
    s.name = path.stem
    return s


def to_monthly(s: pd.Series, agg: str) -> pd.Series:
    """Month-end index. Monthly FRED series are dated the 1st of their reference month."""
    g = s.resample("ME")
    out = g.last() if agg == "last" else g.mean()
    return out.dropna()


def write_fred_csv(s: pd.Series, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    s.rename(path.stem).to_frame().to_csv(path)
