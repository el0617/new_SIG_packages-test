"""Scenario priors for the analysts' Week 5 matrix."""

from __future__ import annotations

import pandas as pd

TODO = "Phase 4 (M5): write scenario priors"

SCENARIOS = ("recession", "soft_landing", "reacceleration", "inflation_shock")


def scenario_prior(p_recession: float, regime_shares: pd.Series) -> pd.Series:
    """Recession gets p_recession; regime shares split the rest. Index = SCENARIOS, sums to 1."""
    raise NotImplementedError(TODO)
