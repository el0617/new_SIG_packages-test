"""Covariance of monthly sector returns (monthly units; annualize with x12)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

from sigtd.data.panel import Panel


def ledoit_wolf(panel: Panel, as_of: pd.Timestamp, months: int = 60) -> pd.DataFrame:
    r = panel.returns_through(as_of).tail(months).dropna()
    lw = LedoitWolf().fit(r.values)
    return pd.DataFrame(lw.covariance_, index=r.columns, columns=r.columns)


def ewma(panel: Panel, as_of: pd.Timestamp, halflife_months: int = 24) -> pd.DataFrame:
    r = panel.returns_through(as_of).dropna()
    w = 0.5 ** (np.arange(len(r))[::-1] / halflife_months)
    w = w / w.sum()
    x = r - (r.values * w[:, None]).sum(axis=0)
    cov = (x.values * w[:, None]).T @ x.values
    return pd.DataFrame(cov, index=r.columns, columns=r.columns)
