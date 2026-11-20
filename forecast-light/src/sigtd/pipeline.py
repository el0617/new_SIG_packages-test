"""The weekly run, end to end (forecast-light).

    data -> regime context -> recession probability -> TE target -> insurance -> risk -> brief

Only one number is forecast: the recession probability. It decides how much insurance to hold.
"""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import build_panel
from sigtd.portfolio import risk_budget
from sigtd.probability.recession import recession_probability
from sigtd.probability.scenarios import scenario_prior
from sigtd.regime.spec_grid import regime_shares
from sigtd.report.brief import render_brief
from sigtd.risk.stress import historical_replays
from sigtd.risk.tracking_error import risk_report


def run_weekly(cfg: Config, as_of: pd.Timestamp) -> None:
    panel = build_panel(cfg)

    shares = regime_shares(panel, as_of, cfg)  # context for the analysts, not a trade signal
    p_rec = recession_probability(panel, as_of, cfg)
    scenarios = scenario_prior(p_rec, shares)

    weights = risk_budget.propose(panel, as_of, cfg, p_recession=p_rec)

    render_brief(
        {
            "regime_shares": shares,
            "p_recession": p_rec,
            "te_target": risk_budget.te_target(p_rec, cfg),
            "scenarios": scenarios,
            "weights": weights,
            "benchmark": panel.benchmark(as_of),
            "risk": risk_report(weights, panel, as_of, cfg),
            "stress": historical_replays(weights, panel, as_of, cfg),
        },
        cfg,
        as_of,
    )
