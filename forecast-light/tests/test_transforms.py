"""M1 acceptance: transforms match hand calculations and never look ahead."""

import numpy as np
import pandas as pd
import pytest

from sigtd.features.transforms import ann3m, zscore_expanding

pytestmark = pytest.mark.xfail(
    raises=NotImplementedError, reason="Phase 1: transforms not written yet"
)


def test_ann3m_matches_hand_calculation():
    s = pd.Series(
        [100.0, 101.0, 102.0, 103.0], index=pd.date_range("2020-01-31", periods=4, freq="ME")
    )
    assert ann3m(s).iloc[-1] == pytest.approx(((103 / 100) ** 4 - 1) * 100)


def test_expanding_zscore_has_no_lookahead():
    s = pd.Series(np.arange(100.0))
    shocked = s.copy()
    shocked.iloc[80:] = 1e6
    a = zscore_expanding(s, min_periods=24)
    b = zscore_expanding(shocked, min_periods=24)
    pd.testing.assert_series_equal(a.iloc[:80], b.iloc[:80])
