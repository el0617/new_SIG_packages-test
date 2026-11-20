"""End-to-end smoke test on the real data cache (skipped when data/raw is empty)."""

import pandas as pd
import pytest

from sigtd.config import ROOT

RAW = ROOT / "data" / "raw"
pytestmark = pytest.mark.skipif(not (RAW / "PAYEMS.csv").exists(), reason="no data cache")


def test_weekly_brief_in_both_modes(cfg, tmp_path, monkeypatch):
    from sigtd.data.panel import build_panel
    from sigtd.pipeline import run_weekly

    panel = build_panel(cfg)
    as_of = pd.Timestamp("2026-11-20")
    bl = run_weekly(cfg, as_of, views=None, panel=panel)
    rb = run_weekly(cfg, as_of, views="none", panel=panel)
    assert bl.exists() and rb.exists()
    assert "Black-Litterman" in bl.read_text()
    assert "Risk-budget fallback" in rb.read_text()


def test_panel_never_shows_unpublished_payrolls(cfg):
    from sigtd.data.panel import build_panel

    panel = build_panel(cfg)
    # September 2026 payrolls (published early October) must be invisible on Sep 30
    assert panel.series("PAYEMS", pd.Timestamp("2026-09-30")).index.max() < pd.Timestamp(
        "2026-09-30"
    )
    assert panel.series("PAYEMS", pd.Timestamp("2026-10-15")).index.max() == pd.Timestamp(
        "2026-09-30"
    )
