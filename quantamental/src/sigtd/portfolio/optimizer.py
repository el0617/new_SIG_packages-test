"""Constrained optimizer (cvxpy). Sized by the tracking-error target, so tau barely matters."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config

TODO = "Phase 5 (M6): write the optimizer"


def optimize(
    mu: pd.Series, cov: pd.DataFrame, benchmark: pd.Series, cfg: Config, te_target: float
) -> pd.Series:
    """max w'mu - delta/2 w'Sigma w  s.t. sum(w)=1, w>=0, |w-b|<=limit, 12 a'Sigma a <= te^2."""
    raise NotImplementedError(TODO)
