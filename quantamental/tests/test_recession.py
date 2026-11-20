"""M5 acceptance."""

import numpy as np
import pandas as pd
import pytest

from sigtd.probability.calibration import brier, brier_skill
from sigtd.probability.recession import make_target, training_window


def test_target_looks_forward_twelve_months():
    idx = pd.date_range("2000-01-31", periods=30, freq="ME")
    usrec = pd.Series(0, index=idx)
    usrec.iloc[20:24] = 1
    y = make_target(usrec, horizon=12)
    assert y.iloc[7] == 0  # months 8..19: no recession
    assert y.iloc[8] == 1  # months 9..20: month 20 is a recession
    assert np.isnan(y.iloc[-1])  # outcome unknown


def test_embargo_drops_recent_labels():
    y = pd.Series(0.0, index=pd.date_range("1990-01-31", periods=200, freq="ME"))
    as_of = y.index[150]
    train = training_window(y, as_of, embargo_months=24)
    assert train.index.max() <= as_of - pd.DateOffset(months=24)


def test_perfect_forecast_has_zero_brier():
    y = np.array([0, 1, 1, 0])
    assert brier(y.astype(float), y) == 0


def test_base_rate_forecast_has_zero_skill():
    y = np.array([0, 0, 0, 1])
    assert brier_skill(np.full(4, y.mean()), y) == pytest.approx(0.0)
