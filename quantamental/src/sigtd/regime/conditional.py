"""Sector relative returns conditional on the regime known at month-end t."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from sigtd.regime.classifier import REGIMES


def conditional_returns(labels: pd.Series, rel: pd.DataFrame) -> pd.DataFrame:
    """Next-month relative return by regime and sector.

    The t-statistic treats each regime *episode* as one observation, because months inside an
    episode are not independent. Cells with fewer than 4 episodes are flagged as not credible.
    """
    nxt = rel.shift(-1)
    idx = labels.index.intersection(nxt.dropna(how="all").index)
    lab, nxt = labels.reindex(idx), nxt.reindex(idx)
    episode = (lab != lab.shift()).cumsum()
    rows = []
    for regime in REGIMES:
        mask = lab == regime
        if mask.sum() == 0:
            continue
        sub, ep = nxt[mask], episode[mask]
        ep_means = sub.groupby(ep).mean()
        k = len(ep_means)
        for sector in rel.columns:
            x = ep_means[sector].dropna()
            if k >= 2 and x.std(ddof=1) > 0:
                t = x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
                p = 2 * stats.t.sf(abs(t), df=len(x) - 1)
            else:
                t, p = np.nan, np.nan
            rows.append(
                {
                    "regime": regime,
                    "sector": sector,
                    "mean_ann_pct": sub[sector].mean() * 1200,
                    "hit_pct": (sub[sector].dropna() > 0).mean() * 100,
                    "months": int(sub[sector].notna().sum()),
                    "episodes": k,
                    "t_episode": t,
                    "p": p,
                }
            )
    out = pd.DataFrame(rows)
    ok = out["p"].notna()
    out["q_bh"] = np.nan
    if ok.any():
        out.loc[ok, "q_bh"] = multipletests(out.loc[ok, "p"], method="fdr_bh")[1]
    out["credible"] = out["episodes"] >= 4
    return out
