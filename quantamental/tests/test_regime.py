"""M2 acceptance."""

import pandas as pd
import pytest

from sigtd.regime.classifier import classify
from sigtd.regime.spec_grid import spec_grid

pytestmark = pytest.mark.xfail(raises=NotImplementedError, reason="Phase 2: regime not written yet")


def test_band_turns_small_readings_into_transition():
    g = pd.Series([0.05, 0.5, 0.5])
    i = pd.Series([0.05, -0.5, 0.5])
    assert list(classify(g, i, band=0.15, sticky=False)) == [
        "Transition",
        "Goldilocks",
        "Reflation",
    ]


def test_grid_has_at_least_nine_specs(cfg):
    assert len(spec_grid(cfg)) >= 9
