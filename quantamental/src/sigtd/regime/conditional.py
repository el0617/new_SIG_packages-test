"""Sector excess returns conditional on the regime known at month-end t."""

from __future__ import annotations

import pandas as pd

TODO = "Phase 2 (M2): write conditional returns"


def conditional_returns(labels: pd.Series, excess: pd.DataFrame) -> pd.DataFrame:
    """Next-month excess return by regime and sector: mean, hit rate, episode-clustered t,
    block-bootstrap 90% interval, BH q-value, number of episodes (flag < 4 as not credible)."""
    raise NotImplementedError(TODO)
