"""Black-Litterman posterior with Idzorek confidences."""

from __future__ import annotations

import pandas as pd

TODO = "Phase 5 (M6): write the posterior"


def posterior(
    pi: pd.Series,
    cov: pd.DataFrame,
    P: pd.DataFrame,
    Q: pd.Series,
    confidence: pd.Series,
    tau: float = 0.05,
) -> pd.Series:
    """mu_BL. With no views, return pi exactly. Solve each view's omega from its confidence."""
    raise NotImplementedError(TODO)
