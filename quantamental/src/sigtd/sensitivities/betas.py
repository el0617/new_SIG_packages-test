"""Sector relative returns regressed on macro factor changes, with HAC errors.

These betas are for risk and scenarios. They only forecast returns if you can forecast the factors.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from sigtd.config import Config
from sigtd.data.panel import Panel
from sigtd.regime.classifier import growth_composite


def factor_changes(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """Monthly changes of the configured factors, point-in-time."""
    s = lambda sid: panel.series(sid, as_of)  # noqa: E731
    candidates = {
        "d_10y": s("GS10").diff(),
        "d_slope": (s("GS10") - s("TB3MS")).diff(),
        "oil": s("DCOILWTICO").pct_change(fill_method=None),
        "dollar": s("DTWEXBGS").pct_change(fill_method=None),
        "d_credit": (s("BAA") - s("GS10")).diff(),
        "growth": growth_composite(panel, as_of, cfg, smooth_months=1).diff(),
        "d_breakeven": s("T5YIFR").diff(),
    }
    wanted = list(cfg.get("sensitivities.factors"))
    return pd.DataFrame({k: v for k, v in candidates.items() if k in wanted})


def _design(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    F = factor_changes(panel, as_of, cfg).dropna()
    rel = panel.relative_returns_through(as_of)
    idx = F.index.intersection(rel.dropna(how="all").index)
    return F.loc[idx], rel.loc[idx]


def sector_betas(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """Long frame: sector, factor, beta, t_stat (HAC), vif, n. Full sample up to as_of."""
    F, rel = _design(panel, as_of, cfg)
    X = sm.add_constant(F)
    vif = {
        c: variance_inflation_factor(X.values, i) for i, c in enumerate(X.columns) if c != "const"
    }
    rows = []
    for sector in rel.columns:
        y = rel[sector].dropna()
        xs = X.loc[y.index]
        fit = sm.OLS(y, xs).fit(
            cov_type="HAC", cov_kwds={"maxlags": cfg.get("sensitivities.hac_lags")}
        )
        for f in F.columns:
            rows.append(
                {
                    "sector": sector,
                    "factor": f,
                    "beta": fit.params[f],
                    "t_stat": fit.tvalues[f],
                    "vif": vif[f],
                    "n": int(fit.nobs),
                }
            )
    return pd.DataFrame(rows)


def beta_matrix(betas: pd.DataFrame) -> pd.DataFrame:
    return betas.pivot(index="sector", columns="factor", values="beta")


def rolling_betas(
    panel: Panel, as_of: pd.Timestamp, cfg: Config, factor: str = "growth"
) -> pd.DataFrame:
    """Univariate rolling beta of each sector's relative return to one factor (dates x sectors)."""
    f = factor_changes(panel, as_of, cfg)[factor]
    rel = panel.relative_returns_through(as_of)
    idx = f.dropna().index.intersection(rel.index)
    f, rel = f.loc[idx], rel.loc[idx]
    n = int(cfg.get("sensitivities.rolling_months"))
    cov = rel.rolling(n, min_periods=n // 2).cov(f)
    return cov.div(f.rolling(n, min_periods=n // 2).var(), axis=0)


def split_sample_flags(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """Sectors x factors: True where a beta changes sign between the two halves of the sample."""
    F, rel = _design(panel, as_of, cfg)
    half = len(F) // 2
    signs = []
    for part in (slice(None, half), slice(half, None)):
        X = sm.add_constant(F.iloc[part])
        b = {s: sm.OLS(rel[s].iloc[part], X, missing="drop").fit().params[F.columns] for s in rel}
        signs.append(np.sign(pd.DataFrame(b).T))
    return signs[0] != signs[1]
