"""Forecast scoring: you are judged on calibration, not on in-sample fit."""

from __future__ import annotations

import numpy as np
import pandas as pd

TODO = "Phase 4 (M5): write calibration metrics"


def brier(p: np.ndarray, y: np.ndarray) -> float:
    raise NotImplementedError(TODO)


def brier_skill(p: np.ndarray, y: np.ndarray) -> float:
    """1 - Brier(p) / Brier(base rate). 0 = no better than always forecasting the base rate."""
    raise NotImplementedError(TODO)


def auc(p: np.ndarray, y: np.ndarray) -> float:
    raise NotImplementedError(TODO)


def reliability_table(p: np.ndarray, y: np.ndarray, bins: int = 10) -> pd.DataFrame:
    """Mean forecast vs observed frequency per probability bin."""
    raise NotImplementedError(TODO)
