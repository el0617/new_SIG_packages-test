"""Ex-ante tracking error and its Euler split (annualized from monthly covariance)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel
from sigtd.portfolio.covariance import ledoit_wolf
from sigtd.risk.var import active_var_cvar


def tracking_error(active: pd.Series, cov: pd.DataFrame) -> float:
    """sqrt(12 a' Sigma a)."""
    a = active.reindex(cov.index).fillna(0.0).values
    return float(np.sqrt(max(12 * a @ cov.values @ a, 0.0)))


def mctr(active: pd.Series, cov: pd.DataFrame) -> pd.Series:
    """Marginal contribution: 12 (Sigma a)_i / TE."""
    te = tracking_error(active, cov)
    a = active.reindex(cov.index).fillna(0.0)
    if te == 0:
        return pd.Series(0.0, index=cov.index)
    return pd.Series(12 * cov.values @ a.values / te, index=cov.index)


def contributions(active: pd.Series, cov: pd.DataFrame) -> pd.Series:
    """a_i x MCTR_i. Sums to TE (Euler)."""
    a = active.reindex(cov.index).fillna(0.0)
    return (a * mctr(active, cov)).rename("te_contribution")


def market_betas(panel: Panel, as_of: pd.Timestamp, months: int = 60) -> pd.Series:
    r = panel.returns_through(as_of).tail(months)
    m = panel.market_through(as_of).tail(months)
    return r.apply(lambda col: col.cov(m) / m.var())


def risk_report(weights: pd.Series, panel: Panel, as_of: pd.Timestamp, cfg: Config) -> dict:
    """TE, beta to the market, Euler contributions, VaR/CVaR and limit checks."""
    b = panel.benchmark(as_of)
    a = (weights - b).rename("active")
    cov = ledoit_wolf(panel, as_of, months=cfg.get("risk.cov_months"))
    te = tracking_error(a, cov)
    contrib = contributions(a, cov)
    betas = market_betas(panel, as_of)
    alt = {
        f"te_{n}m": tracking_error(a, ledoit_wolf(panel, as_of, months=n))
        for n in cfg.get("risk.cov_alt_months")
    }
    lo, hi = cfg.get("mandate.limits.te_budget")
    limit = cfg.get("mandate.limits.active_weight_pp") / 100
    return {
        "active": a,
        "te": te,
        **alt,
        "beta": float((weights * betas).sum()),
        "benchmark_beta": float((b * betas).sum()),
        "contributions": contrib,
        "var": active_var_cvar(
            a,
            panel.returns_through(as_of),
            horizon_months=cfg.get("risk.var_horizon_months"),
            level=cfg.get("risk.var_level"),
        ),
        "checks": {
            "max |active| <= limit": bool(a.abs().max() <= limit + 1e-9),
            "long only": bool((weights >= -1e-9).all()),
            "weights sum to 1": bool(abs(weights.sum() - 1) < 1e-6),
            f"TE within the {hi:.0%} cap": bool(te <= hi + 1e-9),
        },
        "te_band": (lo, hi),
    }
