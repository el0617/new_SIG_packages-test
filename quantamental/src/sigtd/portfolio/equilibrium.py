"""Implied equilibrium returns: what the benchmark weights 'believe'."""

from __future__ import annotations

import pandas as pd

TODO = "Phase 5 (M6): write reverse optimization"


def implied_returns(cov: pd.DataFrame, benchmark: pd.Series, delta: float) -> pd.Series:
    """pi = delta * Sigma @ w_benchmark."""
    raise NotImplementedError(TODO)
