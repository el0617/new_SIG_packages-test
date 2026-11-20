"""Insurance bets: self-funding active vectors with a stated reason."""

from __future__ import annotations

import pandas as pd


def bet_vector(longs: list[str], benchmark: pd.Series) -> pd.Series:
    """+1 unit split equally across `longs`, funded pro rata from every other sector by benchmark
    weight. Sums to zero. Scale it afterwards with risk_budget.scale_to_te."""
    v = pd.Series(0.0, index=benchmark.index)
    v[longs] = 1.0 / len(longs)
    others = benchmark.drop(longs)
    v[others.index] = -others / others.sum()
    return v.rename("active")
