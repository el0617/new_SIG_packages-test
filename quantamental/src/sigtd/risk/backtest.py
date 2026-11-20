"""Walk-forward backtest of the systematic pipeline.

Analysts' views cannot be backtested (they did not exist in the past), so this tests three
systematic engines: signals through Black-Litterman, the risk-budget fallback, and the benchmark.
Every month the engine receives a panel truncated at as_of, so look-ahead is impossible.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd
import statsmodels.api as sm

from sigtd.config import Config
from sigtd.data.panel import Panel, build_panel

Engine = Callable[[Panel, pd.Timestamp], pd.Series]


def walk_forward(
    cfg: Config,
    start: str | None = None,
    engine: Engine | None = None,
    panel: Panel | None = None,
) -> pd.DataFrame:
    """For each month-end t from `start`: weights = engine(panel cut at t, t); hold over t+1;
    charge risk.cost_bp_one_way on traded value.

    Returns one row per holding month: weights_date, port_return, bench_return, turnover, cost,
    active_return (after costs).
    """
    panel = panel or build_panel(cfg)
    engine = engine or signals_bl_engine(cfg)
    start = pd.Timestamp(start or cfg.get("backtest.start"))
    dates = panel.returns.index
    cost_rate = cfg.get("risk.cost_bp_one_way") / 1e4
    rows, prev = [], None
    for t, t_next in zip(dates[:-1], dates[1:], strict=True):
        if t < start:
            continue
        cut = panel.truncate(t)
        w = engine(cut, t).reindex(panel.returns.columns).fillna(0.0)
        b = cut.benchmark(t).reindex(panel.returns.columns).fillna(0.0)
        r = panel.returns.loc[t_next].fillna(0.0)
        # Costs come from changing the active bets. The benchmark proxy is fixed-weight, so
        # charging for its monthly rebalancing would be an artefact of the proxy.
        active = w - b
        traded = float((active - prev).abs().sum()) if prev is not None else 0.0
        cost = traded * cost_rate
        port, bench = float(w @ r), float(b @ r)
        rows.append(
            {
                "month": t_next,
                "weights_date": t,
                "port_return": port,
                "bench_return": bench,
                "turnover": traded / 2,
                "cost": cost,
                "active_return": port - bench - cost,
            }
        )
        prev = active
    return pd.DataFrame(rows).set_index("month")


def performance_stats(active_returns: pd.Series, nw_lags: int = 3) -> dict[str, float]:
    a = active_returns.dropna()
    fit = sm.OLS(a.values, np.ones(len(a))).fit(cov_type="HAC", cov_kwds={"maxlags": nw_lags})
    cum = a.cumsum()
    te = a.std() * np.sqrt(12)
    return {
        "active_return_ann_pct": a.mean() * 1200,
        "tracking_error_ann_pct": te * 100,
        "information_ratio": (a.mean() * 12 / te) if te > 0 else np.nan,
        "t_stat_nw": float(fit.tvalues[0]),
        "hit_rate_pct": (a > 0).mean() * 100,
        "max_relative_drawdown_pct": float((cum - cum.cummax()).min() * 100),
        "months": float(len(a)),
    }


# ---------------------------------------------------------------- engines


def benchmark_engine(panel: Panel, as_of: pd.Timestamp) -> pd.Series:
    return panel.benchmark(as_of)


def risk_budget_engine(cfg: Config) -> Engine:
    from sigtd.portfolio.risk_budget import propose
    from sigtd.probability.recession import recession_probability

    def run(panel: Panel, as_of: pd.Timestamp) -> pd.Series:
        return propose(panel, as_of, cfg, recession_probability(panel, as_of, cfg))

    return run


def signals_bl_engine(cfg: Config) -> Engine:
    """Composite of every available signal -> Grinold views at a pre-registered IC and
    confidence -> Black-Litterman -> optimizer. No scorecard information is used (it would be
    look-ahead)."""
    from sigtd.portfolio.black_litterman import posterior
    from sigtd.portfolio.covariance import ledoit_wolf
    from sigtd.portfolio.equilibrium import implied_returns
    from sigtd.portfolio.optimizer import optimize
    from sigtd.portfolio.views import signal_views, to_pq
    from sigtd.signals.library import composite, compute_all

    def run(panel: Panel, as_of: pd.Timestamp) -> pd.Series:
        b = panel.benchmark(as_of)
        cov = ledoit_wolf(panel, as_of, months=cfg.get("risk.cov_months"))
        sigma = panel.relative_returns_through(as_of).tail(60).std() * np.sqrt(12)
        views = signal_views(
            composite(compute_all(panel, as_of, cfg)),
            sigma,
            ic=cfg.get("backtest.signal_ic_prior"),
            confidence_1to5=cfg.get("backtest.signal_confidence"),
            threshold_z=cfg.get("signals.view_threshold_z"),
        )
        pi = implied_returns(cov, b, cfg.get("black_litterman.delta"))
        if views.empty:
            return b
        P, Q, conf = to_pq(views, b)
        mu = posterior(pi, cov, P, Q, conf, tau=cfg.get("black_litterman.tau"))
        return optimize(mu, cov, b, cfg, te_target=cfg.get("black_litterman.te_target"))

    return run
