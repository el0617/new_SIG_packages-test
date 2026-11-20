"""M6/M7 acceptance: insurance sizing and tracking-error arithmetic."""

import pandas as pd
import pytest

from sigtd.portfolio.insurance import bet_vector
from sigtd.portfolio.risk_budget import scale_to_te, te_target
from sigtd.risk.tracking_error import contributions, tracking_error

pytestmark = pytest.mark.xfail(
    raises=NotImplementedError, reason="Phases 5-6: risk budget and TE not written yet"
)

DEFENSIVE = ["cons_staples", "utilities", "health_care"]


def test_bet_is_self_funding(benchmark):
    v = bet_vector(DEFENSIVE, benchmark)
    assert v.sum() == pytest.approx(0.0)
    assert (v[DEFENSIVE] > 0).all()


def test_scaled_bet_hits_te_target(benchmark, cov):
    a = scale_to_te(bet_vector(DEFENSIVE, benchmark), cov, 0.025)
    assert tracking_error(a, cov) == pytest.approx(0.025, rel=1e-6)


def test_te_target_rises_with_recession_risk_and_is_bounded(cfg):
    ts = [te_target(p, cfg) for p in (0.0, 0.2, 0.4, 0.6, 1.0)]
    assert ts == sorted(ts)
    assert min(ts) == pytest.approx(cfg.get("insurance.te_min"))
    assert max(ts) == pytest.approx(cfg.get("insurance.te_max"))


def test_euler_contributions_sum_to_te(cov, sectors):
    a = pd.Series(0.0, index=sectors)
    a["energy"], a["info_tech"] = 0.03, -0.03
    assert contributions(a, cov).sum() == pytest.approx(tracking_error(a, cov))
