"""Implied equilibrium returns: what the benchmark weights 'believe' (annual units)."""

from __future__ import annotations

import pandas as pd


def implied_returns(cov: pd.DataFrame, benchmark: pd.Series, delta: float) -> pd.Series:
    """pi = delta * Sigma_annual @ w_benchmark, with Sigma_annual = 12 x monthly covariance."""
    b = benchmark.reindex(cov.index)
    return (delta * 12 * cov @ b).rename("pi")
