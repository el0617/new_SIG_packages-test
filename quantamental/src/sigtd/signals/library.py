"""Pre-registered signals. Each returns a sector score vector for any as_of, z-scored across
sectors that month. Do not add signals after seeing results."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel
from sigtd.regime.classifier import REGIMES, growth_composite
from sigtd.regime.spec_grid import baseline_labels, regime_shares
from sigtd.sensitivities.betas import rolling_betas

Signal = Callable[[Panel, pd.Timestamp, Config], pd.Series]


class DataUnavailable(RuntimeError):
    """The signal's inputs are not in the panel (e.g. Bloomberg exports missing)."""


def cross_sectional_z(x: pd.Series) -> pd.Series:
    x = x.dropna()
    sd = x.std()
    return (x - x.mean()) / sd if sd and sd > 0 else x * 0.0


def momentum_12_1(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Cumulative relative return t-12..t-1, skipping the latest month (Moskowitz-Grinblatt)."""
    rel = panel.relative_returns_through(as_of)
    if len(rel) < 13:
        raise DataUnavailable("momentum needs 13 months of returns")
    window = rel.iloc[-13:-1]
    return cross_sectional_z(np.expm1(np.log1p(window).sum(min_count=12)))


def revision_breadth(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """(up - down) / (up + down) forward-EPS revisions, 3-month average (Bloomberg)."""
    up, down = panel.extras.get("sector_rev_up"), panel.extras.get("sector_rev_down")
    if up is None or down is None:
        raise DataUnavailable("needs Bloomberg revision counts (sector_rev_up/down.csv)")
    breadth = (up - down) / (up + down)
    k = int(cfg.get("signals.revision_breadth.smooth_months", 3))
    return cross_sectional_z(breadth.loc[:as_of].tail(k).mean())


def relative_valuation(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Minus z-score of forward P/E relative to the market vs its own trailing 10 years."""
    pe = panel.extras.get("sector_fwd_pe")
    if pe is None or "market" not in pe.columns:
        raise DataUnavailable(
            "needs Bloomberg forward P/E (sector_fwd_pe.csv with a market column)"
        )
    rel_pe = pe.drop(columns="market").div(pe["market"], axis=0).loc[:as_of]
    hist = rel_pe.tail(int(cfg.get("signals.relative_valuation.history_months", 120)))
    return cross_sectional_z(-(hist.iloc[-1] - hist.mean()) / hist.std())


def regime_conditional(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Average next-month relative return in the current regime mix, estimated on data before
    as_of only and shrunk toward zero."""
    labels = baseline_labels(panel, as_of, cfg)
    rel = panel.relative_returns_through(as_of)
    nxt = rel.shift(-1)
    idx = labels.index.intersection(nxt.dropna(how="all").index)
    if len(idx) < 60:
        raise DataUnavailable("regime_conditional needs 60 labelled months")
    means = nxt.loc[idx].groupby(labels.loc[idx]).mean().reindex(REGIMES)
    shares = regime_shares(panel, as_of, cfg)
    expected = (means.fillna(0.0).T * shares).sum(axis=1)
    return cross_sectional_z(expected * float(cfg.get("signals.regime_conditional.shrink", 0.5)))


def macro_tilt(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Rolling growth beta x the growth composite's latest 3-month change."""
    betas = rolling_betas(panel, as_of, cfg, factor="growth")
    g = growth_composite(panel, as_of, cfg, smooth_months=1)
    if betas.dropna(how="all").empty or len(g) < 4:
        raise DataUnavailable("macro_tilt needs rolling betas and 4 months of growth data")
    return cross_sectional_z(betas.dropna(how="all").iloc[-1] * (g.iloc[-1] - g.iloc[-4]))


SIGNALS: dict[str, Signal] = {
    "momentum_12_1": momentum_12_1,
    "revision_breadth": revision_breadth,
    "relative_valuation": relative_valuation,
    "regime_conditional": regime_conditional,
    "macro_tilt": macro_tilt,
}


def compute_all(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> dict[str, pd.Series]:
    """Every signal that has its data; unavailable ones are skipped."""
    out = {}
    for name, fn in SIGNALS.items():
        try:
            out[name] = fn(panel, as_of, cfg)
        except DataUnavailable:
            continue
    return out


def composite(scores: dict[str, pd.Series], names: list[str] | None = None) -> pd.Series:
    """Equal-weight average of the chosen signals' z-scores, re-standardized."""
    use = [scores[n] for n in (names or list(scores)) if n in scores]
    if not use:
        return pd.Series(dtype=float)
    return cross_sectional_z(pd.concat(use, axis=1).mean(axis=1))
