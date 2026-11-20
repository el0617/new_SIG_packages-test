"""Analog regimes (Mulliner, Harvey et al., 'Regimes', JPM 2026): find past months whose
economic state looks most like today's, without presupposing regime definitions."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel
from sigtd.features.transforms import yoy


def state_matrix(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """Economic state variables up to as_of, z-scored on data up to as_of only."""
    s = lambda sid: panel.series(sid, as_of)  # noqa: E731
    m = panel.market_through(as_of)
    candidates = {
        "market_12m": np.expm1(np.log1p(m).rolling(12).sum()),
        "term_spread": s("GS10") - s("TB3MS"),
        "oil_yoy": yoy(s("DCOILWTICO")),
        "gs10_12m_change": s("GS10").diff(12),
        "vix": s("VIXCLS"),
        "claims_yoy": yoy(s("ICSA")),
        "nfci": s("NFCI"),
    }
    wanted = list(cfg.get("similarity.variables"))
    df = pd.DataFrame({k: v for k, v in candidates.items() if k in wanted}).dropna()
    return (df - df.mean()) / df.std()


def distances(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Summed squared z-score distance of every past month to the latest month."""
    z = state_matrix(panel, as_of, cfg)
    exclude = int(cfg.get("similarity.exclude_recent_months", 36))
    hist = z.iloc[:-exclude] if len(z) > exclude else z.iloc[:0]
    return ((hist - z.iloc[-1]) ** 2).sum(axis=1).rename("distance")


def similar_periods(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DatetimeIndex:
    d = distances(panel, as_of, cfg)
    if d.empty:
        return pd.DatetimeIndex([])
    return d.index[d <= d.quantile(cfg.get("similarity.quantile"))]


def analog_returns(
    panel: Panel, as_of: pd.Timestamp, cfg: Config, horizon: int = 12
) -> pd.DataFrame:
    """Average next-`horizon`-month relative return after analog months vs after the most
    dissimilar months ('anti-regimes'), annualized percent."""
    d = distances(panel, as_of, cfg)
    rel = panel.relative_returns_through(as_of)
    fwd = np.expm1(np.log1p(rel).rolling(horizon).sum().shift(-horizon)) * 100 * 12 / horizon
    q = cfg.get("similarity.quantile")
    near = d.index[d <= d.quantile(q)].intersection(fwd.dropna(how="all").index)
    far = d.index[d >= d.quantile(1 - q)].intersection(fwd.dropna(how="all").index)
    return pd.DataFrame(
        {"analogs": fwd.loc[near].mean(), "anti_regimes": fwd.loc[far].mean()}
    ).rename_axis("sector")
