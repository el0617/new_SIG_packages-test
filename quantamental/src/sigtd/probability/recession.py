"""Recession probability 12 months ahead (Estrella-Mishkin lineage), estimated out of sample."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from sigtd.config import Config
from sigtd.data.panel import Panel


def make_target(usrec: pd.Series, horizon: int = 12) -> pd.Series:
    """y_t = 1 if any month in t+1..t+horizon is a recession month; NaN where unknown."""
    fwd = pd.concat([usrec.shift(-k) for k in range(1, horizon + 1)], axis=1)
    y = fwd.max(axis=1).astype(float)
    y[usrec.shift(-horizon).isna()] = np.nan
    return y.rename("recession_within_h")


def training_window(target: pd.Series, as_of: pd.Timestamp, embargo_months: int) -> pd.Series:
    """Labels usable at as_of: drop the last `embargo_months` (NBER dates recessions late)."""
    cutoff = pd.Timestamp(as_of) - pd.DateOffset(months=embargo_months)
    return target.loc[:cutoff].dropna()


def features(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """Term spread (10y - 3m), credit spread (Baa - 10y), 6-month % change in initial claims."""
    s = lambda sid: panel.series(sid, as_of)  # noqa: E731
    claims = s("ICSA")
    X = pd.DataFrame(
        {
            "term_spread": s("GS10") - s("TB3MS"),
            "credit_spread": s("BAA") - s("GS10"),
            "claims_6m_change": (claims / claims.shift(6) - 1) * 100,
        }
    )
    return X.dropna()


def _fit_predict(X: pd.DataFrame, y: pd.Series, x_now: pd.DataFrame) -> float:
    scaler = StandardScaler().fit(X)
    model = LogisticRegression(C=10.0, max_iter=1000).fit(scaler.transform(X), y.astype(int))
    return float(model.predict_proba(scaler.transform(x_now))[0, 1])


def recession_probability(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> float:
    """Fit the logit on the expanding, embargoed window and predict for the latest month."""
    key = ("p_rec", pd.Timestamp(as_of))
    if key in panel._memo:
        return panel._memo[key]
    X = features(panel, as_of, cfg)
    usrec = panel.series("USREC", as_of)
    y = make_target(usrec, cfg.get("recession.horizon_months"))
    y = training_window(y, as_of, cfg.get("recession.embargo_months"))
    y = y.loc[cfg.get("recession.train_start") :]
    common = X.index.intersection(y.index)
    if X.empty or len(common) < 60 or y.loc[common].nunique() < 2:
        warnings.warn("not enough history to fit the recession model", stacklevel=2)
        p = float("nan")
    else:
        p = _fit_predict(X.loc[common], y.loc[common], X.iloc[[-1]])
    panel._memo[key] = p
    return p


def out_of_sample_path(panel: Panel, cfg: Config, start: str | None = None) -> pd.Series:
    """recession_probability at every month-end from `start`: the series you score and plot."""
    start = start or cfg.get("recession.oos_start")
    end = panel.vintages["realtime_start"].max()
    dates = pd.date_range(start, end, freq="ME")
    return pd.Series(
        [recession_probability(panel, d, cfg) for d in dates], index=dates, name="p_recession"
    )
