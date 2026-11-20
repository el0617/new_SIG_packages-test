"""Null-result rule: no confident view -> forecast-light risk-budget mode."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config

BLACK_LITTERMAN = "black_litterman"
RISK_BUDGET = "risk_budget"


def choose_mode(views: pd.DataFrame, cfg: Config) -> str:
    """BLACK_LITTERMAN if any view has confidence >= black_litterman.min_confidence_for_views."""
    if views is None or views.empty:
        return RISK_BUDGET
    threshold = cfg.get("black_litterman.min_confidence_for_views")
    return BLACK_LITTERMAN if (views["confidence_1to5"] >= threshold).any() else RISK_BUDGET
