"""Growth and inflation composites and the quadrant classifier (Investment Clock lineage)."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel
from sigtd.data.registry import load_registry
from sigtd.features.transforms import ann6m, apply_transform, zscore

REGIMES = ("Goldilocks", "Reflation", "Stagflation", "Slowdown", "Transition")
QUADRANT = {
    (True, False): "Goldilocks",  # growth up, inflation down
    (True, True): "Reflation",
    (False, True): "Stagflation",
    (False, False): "Slowdown",
}
GROWTH_UP = {"Goldilocks", "Reflation"}
INFLATION_UP = {"Reflation", "Stagflation"}


def _spec(cfg: Config, spec: dict) -> tuple[int | str, int, int]:
    window = spec.get("window_months", cfg.get("regime.window_months"))
    smooth = int(spec.get("smooth_months", cfg.get("regime.smooth_months")))
    min_periods = int(cfg.get("regime.min_periods", 60))
    return window, smooth, min_periods


def growth_composite(panel: Panel, as_of: pd.Timestamp, cfg: Config, **spec) -> pd.Series:
    """Average z-score of the growth block, with a minimum-components rule, then smoothed."""
    window, smooth, min_periods = _spec(cfg, spec)
    reg = load_registry(cfg)
    snap = panel.as_of(as_of)
    ids = [s for s in reg.index[reg["block"] == "growth"] if s in snap.columns]
    zs = {}
    for sid in ids:
        x = apply_transform(snap[sid].dropna(), reg.loc[sid, "transform"])
        zs[sid] = zscore(x, window, min_periods).clip(-3, 3)
    if not zs:
        return pd.Series(dtype=float, name="growth")
    df = pd.DataFrame(zs)
    comp = df.mean(axis=1).where(df.notna().sum(axis=1) >= min(3, len(zs)))
    return comp.rolling(smooth, min_periods=1).mean().dropna().rename("growth")


def inflation_composite(panel: Panel, as_of: pd.Timestamp, cfg: Config, **spec) -> pd.Series:
    """6-month annualized core CPI and core PCE minus their anchors, scaled by their own
    volatility, merged into one block."""
    window, smooth, min_periods = _spec(cfg, spec)
    snap = panel.as_of(as_of)
    zs = {}
    for sid, anchor in dict(cfg.get("regime.inflation_anchor")).items():
        if sid not in snap.columns:
            continue
        x = ann6m(snap[sid].dropna())
        dev = x - float(anchor)
        if window == "expanding":
            scale = x.expanding(min_periods=min_periods).std()
        else:
            scale = x.rolling(int(window), min_periods=min_periods).std()
        zs[sid] = (dev / scale).clip(-3, 3)
    if not zs:
        return pd.Series(dtype=float, name="inflation")
    comp = pd.DataFrame(zs).mean(axis=1)
    return comp.rolling(smooth, min_periods=1).mean().dropna().rename("inflation")


def classify(growth: pd.Series, inflation: pd.Series, band: float, sticky: bool) -> pd.Series:
    """Label each month. Inside the neutral band on either axis -> Transition, unless sticky and
    the previous quadrant is still consistent with every axis outside the band (hysteresis)."""
    df = pd.concat({"g": growth, "i": inflation}, axis=1).dropna()
    labels, prev = [], None
    for g, i in zip(df["g"], df["i"], strict=True):
        g_clear, i_clear = abs(g) >= band, abs(i) >= band
        if g_clear and i_clear:
            label = QUADRANT[(g > 0, i > 0)]
        elif sticky and prev in QUADRANT.values():
            consistent = (not g_clear or (g > 0) == (prev in GROWTH_UP)) and (
                not i_clear or (i > 0) == (prev in INFLATION_UP)
            )
            label = prev if consistent else "Transition"
        else:
            label = "Transition"
        labels.append(label)
        prev = label
    return pd.Series(labels, index=df.index, name="regime", dtype=object)
