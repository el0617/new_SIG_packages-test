"""Forecast-light construction: spend a tracking-error budget on insurance, sized by recession risk.

In this repo it is the fallback ('risk-budget mode') when no view is confident.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel
from sigtd.portfolio.covariance import ledoit_wolf
from sigtd.portfolio.insurance import bet_vector
from sigtd.risk.tracking_error import tracking_error


def te_target(p_recession: float, cfg: Config) -> float:
    """Linear in p between insurance.p_low and p_high, from te_min to te_max, clipped."""
    lo, hi = cfg.get("insurance.te_min"), cfg.get("insurance.te_max")
    p_lo, p_hi = cfg.get("insurance.p_low"), cfg.get("insurance.p_high")
    p = 0.0 if p_recession is None or np.isnan(p_recession) else float(p_recession)
    x = np.clip((p - p_lo) / (p_hi - p_lo), 0.0, 1.0)
    return float(lo + x * (hi - lo))


def scale_to_te(active: pd.Series, cov: pd.DataFrame, target: float) -> pd.Series:
    """Scale a self-funding active vector so its annualized tracking error equals `target`."""
    te = tracking_error(active, cov)
    return active * (target / te) if te > 0 else active


def enforce_limits(benchmark: pd.Series, active: pd.Series, cfg: Config) -> pd.Series:
    """Shrink the whole active vector until every |active| <= limit and every weight >= 0."""
    limit = cfg.get("mandate.limits.active_weight_pp") / 100
    scale = min(1.0, limit / active.abs().max()) if active.abs().max() > 0 else 1.0
    a = active * scale
    neg = (benchmark + a) < 0
    if neg.any():
        s = (benchmark[neg] / -a[neg]).min()
        a = a * min(1.0, s)
    w = (benchmark + a).clip(lower=0)
    return (w / w.sum()).rename("weight")


def propose(panel: Panel, as_of: pd.Timestamp, cfg: Config, p_recession: float) -> pd.Series:
    """Benchmark + defensive insurance scaled to the TE target for this recession probability."""
    b = panel.benchmark(as_of)
    cov = ledoit_wolf(panel, as_of, months=cfg.get("risk.cov_months"))
    v = bet_vector(list(cfg.get("insurance.bets.defensive")), b)
    a = scale_to_te(v, cov, te_target(p_recession, cfg))
    return enforce_limits(b, a, cfg)
