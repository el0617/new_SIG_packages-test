"""Run the classifier over a grid of reasonable specifications; report agreement, not one label."""

from __future__ import annotations

import itertools

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel
from sigtd.regime.classifier import REGIMES, classify, growth_composite, inflation_composite


def spec_grid(cfg: Config) -> list[dict]:
    grid = cfg.get("regime.grid")
    return [
        {"window_months": w, "smooth_months": s}
        for w, s in itertools.product(grid["window_months"], grid["smooth_months"])
    ]


def labels_for_spec(panel: Panel, as_of: pd.Timestamp, cfg: Config, spec: dict) -> pd.Series:
    key = ("labels", pd.Timestamp(as_of), tuple(sorted(spec.items())))
    if key not in panel._memo:
        g = growth_composite(panel, as_of, cfg, **spec)
        i = inflation_composite(panel, as_of, cfg, **spec)
        band, sticky = cfg.get("regime.band"), cfg.get("regime.sticky")
        panel._memo[key] = classify(g, i, band=band, sticky=sticky)
    return panel._memo[key]


def baseline_labels(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    spec = {
        "window_months": cfg.get("regime.window_months"),
        "smooth_months": cfg.get("regime.smooth_months"),
    }
    return labels_for_spec(panel, as_of, cfg, spec)


def regime_shares(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.Series:
    """Share of specs placing the latest available month in each regime (sums to 1)."""
    latest = [labels_for_spec(panel, as_of, cfg, s) for s in spec_grid(cfg)]
    latest = [lab.iloc[-1] for lab in latest if not lab.empty]
    counts = pd.Series(latest, dtype=object).value_counts()
    return (counts.reindex(REGIMES, fill_value=0) / max(len(latest), 1)).rename("share")


def real_time_vs_revised(panel: Panel, cfg: Config, start: str = "2001-01-31") -> pd.DataFrame:
    """The label each month-end would have shown in real time vs the label the same month gets
    with all data known today. Disagreement = look-ahead that a revised-data study would hide."""
    last = panel.vintages["realtime_start"].max()
    final = baseline_labels(panel, last, cfg)
    rows = []
    for t in pd.date_range(start, last, freq="ME"):
        rt = baseline_labels(panel, t, cfg)
        if rt.empty:
            continue
        obs = rt.index[-1]
        rows.append(
            {"as_of": t, "obs_month": obs, "real_time": rt.iloc[-1], "revised": final.get(obs)}
        )
    out = pd.DataFrame(rows)
    out["agree"] = out["real_time"] == out["revised"]
    return out
