"""Small matplotlib charts, returned as base64 PNGs for embedding in the brief."""

from __future__ import annotations

import base64
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

BLUE, GREY, RED = "#2a6fdb", "#9aa0a6", "#c0392b"


def _encode(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def _style(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=9)


def active_weights(active_pp: pd.Series, limit_pp: float) -> str:
    s = active_pp.sort_values()
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.barh(s.index, s.values, color=[BLUE if v >= 0 else RED for v in s.values])
    for x in (-limit_pp, limit_pp):
        ax.axvline(x, color=GREY, lw=0.8, ls="--")
    ax.axvline(0, color="black", lw=0.6)
    ax.set_xlabel("Active weight vs benchmark (percentage points)", fontsize=9)
    ax.set_title("Proposed tilts (dashed lines = policy limit)", fontsize=10, loc="left")
    _style(ax)
    return _encode(fig)


def recession_path(p: pd.Series, usrec: pd.Series) -> str:
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    rec = usrec.reindex(p.index).fillna(0)
    ax.fill_between(
        p.index, 0, 1, where=rec > 0, color=GREY, alpha=0.3, lw=0, label="NBER recession"
    )
    ax.plot(p.index, p.values, color=BLUE, lw=1.4, label="Model probability (out of sample)")
    ax.set_ylim(0, 1)
    ax.set_ylabel("P(recession within 12m)", fontsize=9)
    ax.set_title(
        "Recession probability, each month using only data available then", fontsize=10, loc="left"
    )
    ax.legend(fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    _style(ax)
    return _encode(fig)


def bar(series: pd.Series, title: str, xlabel: str, color: str = BLUE) -> str:
    s = series.sort_values()
    fig, ax = plt.subplots(figsize=(6.4, 0.35 * len(s) + 1.0))
    ax.barh(s.index, s.values, color=color)
    ax.axvline(0, color="black", lw=0.6)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(title, fontsize=10, loc="left")
    _style(ax)
    return _encode(fig)


def cumulative(active: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    for name, col in active.items():
        ax.plot(col.index, col.cumsum() * 100, lw=1.3, label=name)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("Cumulative active return (%)", fontsize=9)
    ax.set_title("Walk-forward backtest vs benchmark, after costs", fontsize=10, loc="left")
    ax.legend(fontsize=8, frameon=False)
    _style(ax)
    return _encode(fig)
