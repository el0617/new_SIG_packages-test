"""Tail risk of the active return."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


def active_var_cvar(
    active: pd.Series, returns: pd.DataFrame, horizon_months: int = 3, level: float = 0.95
) -> dict[str, float]:
    """VaR and CVaR of the active return over `horizon_months`, as positive loss fractions.

    Historical: today's active weights applied to every past month, summed over rolling windows.
    Parametric: normal, zero mean, volatility from the same history.
    """
    r = returns[active.index].dropna()
    monthly = r @ active.values
    h = monthly.rolling(horizon_months).sum().dropna()
    cutoff = h.quantile(1 - level)
    sigma = monthly.std() * np.sqrt(horizon_months)
    z = norm.ppf(level)
    return {
        "hist_var": float(-cutoff),
        "hist_cvar": float(-h[h <= cutoff].mean()),
        "param_var": float(z * sigma),
        "param_cvar": float(sigma * norm.pdf(z) / (1 - level)),
    }
