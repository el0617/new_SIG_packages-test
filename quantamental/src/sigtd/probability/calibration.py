"""Forecast scoring: you are judged on calibration, not on in-sample fit."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def brier(p: np.ndarray, y: np.ndarray) -> float:
    p, y = np.asarray(p, float), np.asarray(y, float)
    return float(np.mean((p - y) ** 2))


def brier_skill(p: np.ndarray, y: np.ndarray) -> float:
    """1 - Brier(p) / Brier(base rate). 0 = no better than always forecasting the base rate."""
    y = np.asarray(y, float)
    ref = brier(np.full_like(y, y.mean()), y)
    return float(1 - brier(p, y) / ref) if ref > 0 else float("nan")


def auc(p: np.ndarray, y: np.ndarray) -> float:
    y = np.asarray(y, int)
    return float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else float("nan")


def reliability_table(p: np.ndarray, y: np.ndarray, bins: int = 10) -> pd.DataFrame:
    """Mean forecast vs observed frequency per probability bin."""
    df = pd.DataFrame({"p": np.asarray(p, float), "y": np.asarray(y, float)})
    df["bin"] = pd.cut(df["p"], np.linspace(0, 1, bins + 1), include_lowest=True)
    out = df.groupby("bin", observed=True).agg(
        mean_forecast=("p", "mean"), observed=("y", "mean"), n=("y", "size")
    )
    return out


def score_path(p_path: pd.Series, target: pd.Series) -> dict[str, float]:
    """Brier, Brier skill and AUC of an out-of-sample probability path against realized outcomes."""
    df = pd.concat({"p": p_path, "y": target}, axis=1).dropna()
    return {
        "months_scored": float(len(df)),
        "brier": brier(df["p"], df["y"]),
        "brier_skill": brier_skill(df["p"], df["y"]),
        "auc": auc(df["p"], df["y"]),
    }
