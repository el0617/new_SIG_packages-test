"""M6 acceptance: Black-Litterman, optimizer and the mode switch."""

import pandas as pd
import pytest

from sigtd.portfolio.black_litterman import posterior
from sigtd.portfolio.equilibrium import implied_returns
from sigtd.portfolio.mode import BLACK_LITTERMAN, RISK_BUDGET, choose_mode
from sigtd.portfolio.optimizer import optimize
from sigtd.risk.tracking_error import tracking_error

pytestmark = pytest.mark.xfail(
    raises=NotImplementedError, reason="Phase 5: construction not written yet"
)


def _no_views(sectors):
    return (
        pd.DataFrame(columns=sectors, dtype=float),
        pd.Series(dtype=float),
        pd.Series(dtype=float),
    )


def test_no_views_returns_equilibrium(cov, benchmark):
    pi = implied_returns(cov, benchmark, delta=2.5)
    P, Q, conf = _no_views(list(benchmark.index))
    pd.testing.assert_series_equal(posterior(pi, cov, P, Q, conf), pi, check_names=False)


def test_bullish_view_raises_that_sector(cov, benchmark):
    pi = implied_returns(cov, benchmark, delta=2.5)
    P = pd.DataFrame(
        [[1.0 if s == "energy" else 0.0 for s in benchmark.index]], columns=benchmark.index
    )
    mu = posterior(pi, cov, P, pd.Series([pi["energy"] + 0.05]), pd.Series([0.5]))
    assert mu["energy"] > pi["energy"]


def test_no_views_hold_the_benchmark(cfg, cov, benchmark):
    pi = implied_returns(cov, benchmark, delta=2.5)
    w = optimize(pi, cov, benchmark, cfg, te_target=0.03)
    assert (w - benchmark).abs().max() < 1e-4


def test_limits_hold_under_strong_views(cfg, cov, benchmark):
    mu = pd.Series(0.0, index=benchmark.index)
    mu["energy"], mu["info_tech"] = 0.50, -0.50
    w = optimize(mu, cov, benchmark, cfg, te_target=0.03)
    assert w.sum() == pytest.approx(1.0)
    assert (w >= -1e-9).all()
    assert ((w - benchmark).abs() <= 0.05 + 1e-6).all()
    assert tracking_error(w - benchmark, cov) <= 0.03 + 1e-6


def test_weak_views_trigger_risk_budget_mode(cfg):
    views = pd.DataFrame({"sector": ["energy"], "confidence_1to5": [2], "source": ["signal"]})
    assert choose_mode(views, cfg) == RISK_BUDGET


def test_a_confident_view_enables_black_litterman(cfg):
    views = pd.DataFrame({"sector": ["energy"], "confidence_1to5": [4], "source": ["analyst"]})
    assert choose_mode(views, cfg) == BLACK_LITTERMAN
