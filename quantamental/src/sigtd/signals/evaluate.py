"""Walk-forward evaluation: rank IC, Newey-West t, tercile spreads, turnover, scorecard.

Every score at month-end t is computed from data published by t; it is judged against the
relative return over month t+1.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

from sigtd.config import Config
from sigtd.data.panel import Panel
from sigtd.signals.library import SIGNALS, DataUnavailable, composite
from sigtd.signals.power import min_detectable_ic


def rank_ic(scores: pd.DataFrame, next_returns: pd.DataFrame) -> pd.Series:
    """Monthly Spearman correlation across sectors (rows already aligned: row t = score at t,
    return over t+1)."""
    idx = scores.index.intersection(next_returns.index)
    s, r = scores.loc[idx], next_returns.loc[idx, scores.columns]
    valid = s.notna() & r.notna()
    rs = s.where(valid).rank(axis=1)
    rr = r.where(valid).rank(axis=1)
    rs = rs.sub(rs.mean(axis=1), axis=0)
    rr = rr.sub(rr.mean(axis=1), axis=0)
    num = (rs * rr).sum(axis=1)
    den = np.sqrt((rs**2).sum(axis=1) * (rr**2).sum(axis=1))
    ic = (num / den).where(valid.sum(axis=1) >= 5)
    return ic.dropna().rename("rank_ic")


def ic_summary(ic: pd.Series, nw_lags: int = 1) -> dict[str, float]:
    ic = ic.dropna()
    fit = sm.OLS(ic.values, np.ones(len(ic))).fit(cov_type="HAC", cov_kwds={"maxlags": nw_lags})
    return {
        "mean_ic": float(ic.mean()),
        "t_stat": float(fit.tvalues[0]),
        "ic_ir": float(ic.mean() / ic.std() * np.sqrt(12)),
        "hit_rate": float((ic > 0).mean()),
        "n_months": float(len(ic)),
    }


def tercile_spread(scores: pd.DataFrame, next_returns: pd.DataFrame) -> pd.Series:
    """Top-third minus bottom-third average next-month return, each month."""
    idx = scores.index.intersection(next_returns.index)
    pct = scores.loc[idx].rank(axis=1, pct=True)
    r = next_returns.loc[idx, scores.columns]
    return (r.where(pct > 2 / 3).mean(axis=1) - r.where(pct <= 1 / 3).mean(axis=1)).dropna()


def turnover(scores: pd.DataFrame) -> float:
    """Average share of sectors changing tercile from one month to the next."""
    terc = np.ceil(scores.rank(axis=1, pct=True) * 3)
    changed = (terc != terc.shift()).where(terc.notna() & terc.shift().notna())
    return float(changed.mean(axis=1).dropna().mean())


def signal_history(panel: Panel, cfg: Config, name: str, start: str | None = None) -> pd.DataFrame:
    """Scores at every month-end from `start` (dates x sectors). Raises DataUnavailable."""
    start = start or cfg.get("sample.signal_start")
    end = panel.returns.index[-1]
    SIGNALS[name](panel, end, cfg)  # raises DataUnavailable if the inputs do not exist at all
    rows = {}
    for t in pd.date_range(start, end, freq="ME"):
        try:
            rows[t] = SIGNALS[name](panel, t, cfg)
        except DataUnavailable:  # not enough history yet at this date
            continue
    return pd.DataFrame(rows).T.reindex(columns=panel.returns.columns)


def scorecard(panel: Panel, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One row per pre-registered signal plus the equal-weight composite.

    Returns (scorecard, monthly IC history). Verdicts use a one-sided test with a Holm
    adjustment across the signals that could be tested.
    """
    rel = panel.relative_returns_through(panel.returns.index[-1])
    nxt = rel.shift(-1)
    histories, rows, ics = {}, [], {}
    for name in SIGNALS:
        try:
            histories[name] = signal_history(panel, cfg, name)
        except DataUnavailable as e:
            rows.append({"signal": name, "status": f"data unavailable: {e}"})
    if histories:
        comp = pd.concat(histories, axis=1)
        composite_hist = {t: composite({n: comp.loc[t, n] for n in histories}) for t in comp.index}
        histories["composite"] = pd.DataFrame(composite_hist).T.reindex(columns=rel.columns)

    for name, h in histories.items():
        ic = rank_ic(h, nxt)
        ics[name] = ic
        stats = ic_summary(ic, nw_lags=1)
        n_sectors = int(h.notna().sum(axis=1).median())
        rows.append(
            {
                "signal": name,
                "status": "tested",
                **stats,
                "p_one_sided": float(1 - norm.cdf(stats["t_stat"])),
                "power_threshold_ic": min_detectable_ic(n_sectors, int(stats["n_months"])),
                "tercile_spread_ann_pct": float(tercile_spread(h, nxt).mean() * 1200),
                "turnover": turnover(h),
                "prior": cfg.get(f"signals.{name}.prior", "composite"),
            }
        )
    card = pd.DataFrame(rows).set_index("signal")
    tested = card.index[(card["status"] == "tested") & (card.index != "composite")]
    card["p_holm"] = np.nan
    if len(tested):
        card.loc[tested, "p_holm"] = multipletests(card.loc[tested, "p_one_sided"], method="holm")[
            1
        ]
    card.loc["composite", "p_holm"] = (
        card.loc["composite", "p_one_sided"] if "composite" in card.index else np.nan
    )

    def verdict(r: pd.Series) -> str:
        if r["status"] != "tested":
            return "none"
        if r["mean_ic"] > 0 and r["p_holm"] < 0.05:
            return "oos_value"
        if r["mean_ic"] > 0 and r["t_stat"] >= 1.0:
            return "weak"
        return "none"

    mapping = dict(cfg.get("signals.evidence_to_confidence"))
    card["verdict"] = card.apply(verdict, axis=1)
    card["confidence"] = card["verdict"].map(mapping).astype(int)
    return card, pd.DataFrame(ics)
