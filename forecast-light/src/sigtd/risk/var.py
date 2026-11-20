"""Tail risk of the active return."""

from __future__ import annotations

import pandas as pd

TODO = "Phase 6 (M7): write VaR / CVaR"


def active_var_cvar(
    active: pd.Series, returns: pd.DataFrame, horizon_months: int = 3, level: float = 0.95
) -> dict[str, float]:
    """Historical and parametric VaR and CVaR of the active return over `horizon_months`."""
    raise NotImplementedError(TODO)
