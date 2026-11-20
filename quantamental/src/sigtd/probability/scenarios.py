"""Scenario priors for the analysts' Week 5 matrix."""

from __future__ import annotations

import pandas as pd

SCENARIOS = ("recession", "soft_landing", "reacceleration", "inflation_shock")

# How each regime's share maps onto the non-recession scenarios.
REGIME_TO_SCENARIO = {
    "Goldilocks": {"soft_landing": 1.0},
    "Slowdown": {"soft_landing": 1.0},
    "Reflation": {"reacceleration": 1.0},
    "Stagflation": {"inflation_shock": 1.0},
    "Transition": {"soft_landing": 0.5, "reacceleration": 0.25, "inflation_shock": 0.25},
}


def scenario_prior(p_recession: float, regime_shares: pd.Series) -> pd.Series:
    """Recession gets p_recession; regime shares split the rest. Sums to 1."""
    p = 0.0 if pd.isna(p_recession) else float(p_recession)
    rest = pd.Series(0.0, index=SCENARIOS[1:])
    for regime, share in regime_shares.items():
        for scenario, w in REGIME_TO_SCENARIO.get(regime, {}).items():
            rest[scenario] += share * w
    rest = rest / rest.sum() if rest.sum() > 0 else pd.Series(1 / 3, index=SCENARIOS[1:])
    return pd.concat([pd.Series({"recession": p}), rest * (1 - p)]).rename("probability")
