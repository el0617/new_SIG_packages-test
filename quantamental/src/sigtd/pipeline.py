"""The weekly run, end to end (quantamental).

data -> regime (+ analog cross-check) -> recession probability -> sensitivities
     -> signals + frozen scorecard -> analyst view sheet -> views
     -> mode: Black-Litterman + optimizer, or risk-budget fallback -> risk -> brief
"""

from __future__ import annotations

import pandas as pd

from sigtd.config import ROOT, Config
from sigtd.data.panel import build_panel
from sigtd.portfolio import risk_budget
from sigtd.portfolio.attribution import leave_one_view_out
from sigtd.portfolio.black_litterman import posterior
from sigtd.portfolio.covariance import ledoit_wolf
from sigtd.portfolio.equilibrium import implied_returns
from sigtd.portfolio.mode import BLACK_LITTERMAN, choose_mode
from sigtd.portfolio.optimizer import optimize
from sigtd.portfolio.views import build_views, load_view_sheet, to_pq
from sigtd.probability.recession import recession_probability
from sigtd.probability.scenarios import scenario_prior
from sigtd.regime.similarity import similar_periods
from sigtd.regime.spec_grid import regime_shares
from sigtd.report.brief import render_brief
from sigtd.risk.stress import factor_shocks, historical_replays
from sigtd.risk.tracking_error import risk_report
from sigtd.sensitivities.betas import sector_betas
from sigtd.signals.library import SIGNALS

SCORECARD = ROOT / "outputs" / "scorecard.csv"  # frozen by `make research`, not refit weekly


def run_weekly(cfg: Config, as_of: pd.Timestamp) -> None:
    panel = build_panel(cfg)

    shares = regime_shares(panel, as_of, cfg)
    analogs = similar_periods(panel, as_of, cfg)
    p_rec = recession_probability(panel, as_of, cfg)
    betas = sector_betas(panel, as_of, cfg)

    scores = {name: fn(panel, as_of, cfg) for name, fn in SIGNALS.items()}
    card = pd.read_csv(SCORECARD, index_col=0)
    sheet = load_view_sheet(ROOT / cfg.get("views.sheet"))
    views = build_views(sheet, scores, card)

    cov = ledoit_wolf(panel, as_of, months=cfg.get("risk.cov_months"))
    bench = panel.benchmark(as_of)
    mode = choose_mode(views, cfg)

    if mode == BLACK_LITTERMAN:
        pi = implied_returns(cov, bench, delta=cfg.get("black_litterman.delta"))
        te = cfg.get("black_litterman.te_target")

        def run(v: pd.DataFrame) -> pd.Series:
            P, Q, conf = to_pq(v, cfg.sectors)
            mu = posterior(pi, cov, P, Q, conf, tau=cfg.get("black_litterman.tau"))
            return optimize(mu, cov, bench, cfg, te_target=te)

        weights = run(views)
        attribution = leave_one_view_out(views, run)
    else:
        weights = risk_budget.propose(panel, as_of, cfg, p_recession=p_rec)
        attribution = None

    render_brief(
        {
            "mode": mode,
            "regime_shares": shares,
            "analogs": analogs,
            "p_recession": p_rec,
            "scenarios": scenario_prior(p_rec, shares),
            "scorecard": card,
            "views": views,
            "attribution": attribution,
            "weights": weights,
            "benchmark": bench,
            "risk": risk_report(weights, panel, as_of, cfg),
            "stress": historical_replays(weights, panel, as_of, cfg),
            "factor_shocks": factor_shocks(weights, bench, betas),
        },
        cfg,
        as_of,
    )
