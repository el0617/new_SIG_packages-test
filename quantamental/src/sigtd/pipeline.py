"""The weekly run, end to end (quantamental).

data -> regime (+ analog cross-check) -> recession probability -> sensitivities
     -> signals + frozen scorecard -> analyst view sheet -> views
     -> mode: Black-Litterman + optimizer, or risk-budget fallback -> risk -> brief
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sigtd.config import ROOT, Config
from sigtd.data.panel import Panel, build_panel
from sigtd.portfolio import risk_budget
from sigtd.portfolio.attribution import leave_one_view_out
from sigtd.portfolio.black_litterman import posterior
from sigtd.portfolio.covariance import ledoit_wolf
from sigtd.portfolio.equilibrium import implied_returns
from sigtd.portfolio.mode import BLACK_LITTERMAN, choose_mode
from sigtd.portfolio.optimizer import optimize
from sigtd.portfolio.views import COLUMNS, build_views, load_view_sheet, signal_views, to_pq
from sigtd.probability.calibration import score_path
from sigtd.probability.recession import make_target, out_of_sample_path, recession_probability
from sigtd.probability.scenarios import scenario_prior
from sigtd.regime.similarity import analog_returns
from sigtd.regime.spec_grid import baseline_labels, regime_shares, spec_grid
from sigtd.report.brief import render_brief
from sigtd.risk.stress import factor_shocks, historical_replays
from sigtd.risk.tracking_error import risk_report
from sigtd.sensitivities.betas import beta_matrix, factor_changes, sector_betas
from sigtd.signals.evaluate import scorecard
from sigtd.signals.library import composite, compute_all

OUTPUTS = ROOT / "outputs"
SCORECARD = OUTPUTS / "scorecard.csv"  # frozen by `make research`, not refit weekly


def load_or_build_scorecard(panel: Panel, cfg: Config) -> pd.DataFrame:
    if not SCORECARD.exists():
        warnings.warn("no frozen scorecard: running the signal research now", stacklevel=2)
        card, ics = scorecard(panel, cfg)
        OUTPUTS.mkdir(exist_ok=True)
        card.to_csv(SCORECARD)
        ics.to_csv(OUTPUTS / "signal_ic_history.csv")
    return pd.read_csv(SCORECARD, index_col=0)


def resolve_views(cfg: Config, views: str | None) -> tuple[pd.DataFrame, bool]:
    """Returns (sheet, is_demo). views=None: the real sheet if it exists, else the demo sheet.
    views="none": no analyst views. Otherwise a path."""
    if views == "none":
        return pd.DataFrame(columns=list(COLUMNS)), False
    if views:
        return load_view_sheet(Path(views)), False
    real = ROOT / cfg.get("views.sheet")
    if real.exists():
        return load_view_sheet(real), False
    return load_view_sheet(ROOT / cfg.get("views.demo_sheet")), True


def run_weekly(
    cfg: Config, as_of: pd.Timestamp, views: str | None = None, panel: Panel | None = None
) -> Path:
    panel = panel or build_panel(cfg)

    # macro state
    shares = regime_shares(panel, as_of, cfg)
    regime_month = baseline_labels(panel, as_of, cfg).index[-1]
    p_rec = recession_probability(panel, as_of, cfg)
    p_path = out_of_sample_path(panel, cfg).loc[:as_of]
    usrec = panel.series("USREC", as_of)
    p_scores = score_path(p_path, make_target(usrec, cfg.get("recession.horizon_months")))
    betas = sector_betas(panel, as_of, cfg)
    growth_sd = factor_changes(panel, as_of, cfg).std()

    # evidence and views
    card = load_or_build_scorecard(panel, cfg)
    scores = compute_all(panel, as_of, cfg)
    qualifying = [
        n for n in card.index if n in scores and card.loc[n, "confidence"] > 0 and n != "composite"
    ]
    sigma = panel.relative_returns_through(as_of).tail(60).std() * np.sqrt(12)
    sig_views = signal_views(
        composite(scores, qualifying) if qualifying else pd.Series(dtype=float),
        sigma,
        ic=float(card.loc[qualifying, "mean_ic"].mean()) if qualifying else 0.0,
        confidence_1to5=int(card.loc[qualifying, "confidence"].min()) if qualifying else 0,
        threshold_z=cfg.get("signals.view_threshold_z"),
    )
    sheet, is_demo = resolve_views(cfg, views)
    view_table = build_views(sheet, sig_views)

    # construction
    cov = ledoit_wolf(panel, as_of, months=cfg.get("risk.cov_months"))
    bench = panel.benchmark(as_of)
    mode = choose_mode(view_table, cfg)
    attribution = None
    if mode == BLACK_LITTERMAN:
        pi = implied_returns(cov, bench, delta=cfg.get("black_litterman.delta"))
        te = cfg.get("black_litterman.te_target")

        def run(v: pd.DataFrame) -> pd.Series:
            if v.empty:
                return bench.rename("weight")
            P, Q, conf = to_pq(v, bench)
            mu = posterior(pi, cov, P, Q, conf, tau=cfg.get("black_litterman.tau"))
            return optimize(mu, cov, bench, cfg, te_target=te)

        weights = run(view_table)
        attribution = leave_one_view_out(view_table, run, cfg.get("mandate.aum_usd"))
    else:
        weights = risk_budget.propose(panel, as_of, cfg, p_recession=p_rec)

    OUTPUTS.mkdir(exist_ok=True)
    pd.DataFrame({"benchmark": bench, "weight": weights}).to_csv(
        OUTPUTS / f"weights_{as_of:%Y-%m-%d}_{mode}.csv"
    )

    backtest = None
    if (OUTPUTS / "backtest_active.csv").exists():
        backtest = {
            "active": pd.read_csv(OUTPUTS / "backtest_active.csv", index_col=0, parse_dates=True),
            "summary": pd.read_csv(OUTPUTS / "backtest_summary.csv", index_col=0),
        }

    return render_brief(
        {
            "mode": mode,
            "demo_views": is_demo and not view_table[view_table["source"] == "analyst"].empty,
            "returns_through": panel.returns_through(as_of).index[-1],
            "regime_shares": shares,
            "regime_specs": spec_grid(cfg),
            "regime_month": regime_month,
            "analogs": analog_returns(panel, as_of, cfg),
            "p_recession": p_rec,
            "te_target_rb": risk_budget.te_target(p_rec, cfg),
            "p_path": p_path,
            "p_scores": p_scores,
            "usrec": usrec,
            "scenarios": scenario_prior(p_rec, shares),
            "scorecard": card,
            "views": view_table,
            "attribution": attribution,
            "weights": weights,
            "benchmark": bench,
            "risk": risk_report(weights, panel, as_of, cfg),
            "stress": historical_replays(weights, panel, as_of, cfg),
            "factor_shocks": factor_shocks(
                weights, bench, beta_matrix(betas), cfg, factor_sd=growth_sd
            ),
            "backtest": backtest,
        },
        cfg,
        as_of,
    )
