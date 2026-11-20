"""Null-result rule: no confident view -> forecast-light risk-budget mode."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config

TODO = "Phase 5 (M6): write the mode switch"

BLACK_LITTERMAN = "black_litterman"
RISK_BUDGET = "risk_budget"


def choose_mode(views: pd.DataFrame, cfg: Config) -> str:
    """BLACK_LITTERMAN if any view has confidence >= black_litterman.min_confidence_for_views,
    else RISK_BUDGET. The brief prints the mode at the top."""
    raise NotImplementedError(TODO)
