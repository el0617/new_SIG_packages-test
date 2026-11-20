"""Macro dashboard: each indicator's latest reading as a percentile of the last 20 years."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sigtd.config import ROOT, Config
from sigtd.data.panel import Panel
from sigtd.data.registry import load_registry
from sigtd.features.transforms import apply_transform


def dashboard_table(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    reg = load_registry(cfg)
    rows = []
    for sid, row in reg.iterrows():
        if row["block"] == "target":
            continue
        s = apply_transform(panel.series(sid, as_of), row["transform"]).dropna()
        if s.empty:
            continue
        hist = s.loc[s.index[-1] - pd.DateOffset(years=20) :]
        rows.append(
            {
                "series": sid,
                "block": row["block"],
                "transform": row["transform"],
                "latest month": f"{s.index[-1]:%Y-%m}",
                "value": s.iloc[-1],
                "3m change": s.iloc[-1] - s.iloc[-4] if len(s) > 3 else float("nan"),
                "percentile (20y)": (hist <= s.iloc[-1]).mean() * 100,
            }
        )
    return pd.DataFrame(rows)


def render_dashboard(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> Path:
    df = dashboard_table(panel, as_of, cfg)

    def shade(v: float) -> str:
        if pd.isna(v):
            return ""
        hue = 10 if v > 80 else 210 if v < 20 else 0
        return f"background-color: hsl({hue}, 70%, 92%)" if hue else ""

    html = (
        df.style.format(precision=2)
        .map(shade, subset=["percentile (20y)"])
        .hide(axis="index")
        .to_html()
    )
    out = ROOT / "reports" / f"dashboard_{as_of:%Y-%m-%d}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"<html><head><meta charset='utf-8'><title>Macro dashboard {as_of:%Y-%m-%d}</title></head>"
        f"<body style='font-family:Helvetica,Arial,sans-serif'><h2>Macro dashboard, data as "
        f"published by {as_of:%Y-%m-%d}</h2>{html}</body></html>"
    )
    return out
