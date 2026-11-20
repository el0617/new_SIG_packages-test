"""M4 acceptance: power arithmetic, no look-ahead, planted signals found, noise rejected."""

import numpy as np
import pandas as pd
import pytest

from sigtd.data.panel import Panel
from sigtd.signals.evaluate import ic_summary, rank_ic
from sigtd.signals.library import momentum_12_1
from sigtd.signals.power import min_detectable_corr, min_detectable_ic

pytestmark = pytest.mark.xfail(
    raises=NotImplementedError, reason="Phase 3: signals not written yet"
)


def test_single_spread_needs_a_large_correlation():
    assert min_detectable_corr(111) == pytest.approx(0.236, abs=0.002)


def test_cross_section_can_detect_a_small_ic():
    assert min_detectable_ic(11, 330) == pytest.approx(0.043, abs=0.002)


def test_momentum_skips_the_latest_month(cfg, panel, sector_returns, benchmark_frame):
    shocked = sector_returns.copy()
    shocked.iloc[-1] += 0.5
    other = Panel(vintages=panel.vintages, returns=shocked, benchmark_weights=benchmark_frame)
    as_of = sector_returns.index[-1]
    pd.testing.assert_series_equal(
        momentum_12_1(panel, as_of, cfg), momentum_12_1(other, as_of, cfg)
    )


def test_planted_signal_is_detected(sector_returns):
    nxt = sector_returns.shift(-1).iloc[:-1]
    noise = np.random.default_rng(1).normal(0, 0.05, nxt.shape)
    scores = nxt + noise
    assert ic_summary(rank_ic(scores, nxt))["t_stat"] > 3


def test_noise_is_rejected_at_about_the_nominal_rate(sector_returns):
    rng = np.random.default_rng(2)
    nxt = sector_returns.shift(-1).iloc[:-1]
    hits = 0
    for _ in range(200):
        scores = pd.DataFrame(rng.normal(size=nxt.shape), index=nxt.index, columns=nxt.columns)
        hits += ic_summary(rank_ic(scores, nxt))["t_stat"] > 1.645
    assert 0.01 <= hits / 200 <= 0.10
