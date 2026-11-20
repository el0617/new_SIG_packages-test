"""M1 acceptance: nothing is visible before it was published."""

import pandas as pd
import pytest

from sigtd.data.panel import Panel

pytestmark = pytest.mark.xfail(raises=NotImplementedError, reason="Phase 1: Panel not written yet")


def _panel(vintages):
    return Panel(vintages=vintages, returns=pd.DataFrame(), benchmark_weights=pd.DataFrame())


def test_value_invisible_before_release(vintages):
    snap = _panel(vintages).as_of(pd.Timestamp("2020-02-10"))
    assert "CPI" not in snap.columns or snap["CPI"].dropna().empty


def test_first_release_then_revision(vintages):
    p = _panel(vintages)
    assert p.as_of(pd.Timestamp("2020-02-20")).loc["2020-01-31", "CPI"] == 100.0
    assert p.as_of(pd.Timestamp("2020-03-15")).loc["2020-01-31", "CPI"] == 100.3


def test_returns_through_stops_at_as_of(panel):
    r = panel.returns_through(pd.Timestamp("2010-06-30"))
    assert r.index.max() <= pd.Timestamp("2010-06-30")
