"""Insurance bets: self-funding active vectors with a stated reason."""

from __future__ import annotations

import pandas as pd

TODO = "Phase 5 (M6): write bet vectors (port the logic of your fall weighting engine)"


def bet_vector(longs: list[str], benchmark: pd.Series) -> pd.Series:
    """+1 unit split equally across `longs`, funded pro rata from every other sector by benchmark
    weight. Sums to zero. Scale it afterwards with risk_budget.scale_to_te."""
    raise NotImplementedError(TODO)
