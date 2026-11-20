"""Synthetic fixtures: small, deterministic, no network."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sigtd.config import load_config
from sigtd.data.panel import Panel

SECTORS = [
    "info_tech",
    "financials",
    "health_care",
    "cons_disc",
    "cons_staples",
    "energy",
    "industrials",
    "materials",
    "utilities",
    "real_estate",
    "comm_services",
]

EMPTY_VINTAGES = pd.DataFrame(
    {
        "series_id": pd.Series(dtype=str),
        "obs_date": pd.Series(dtype="datetime64[ns]"),
        "realtime_start": pd.Series(dtype="datetime64[ns]"),
        "value": pd.Series(dtype=float),
    }
)


@pytest.fixture
def cfg():
    return load_config()


@pytest.fixture
def sectors() -> list[str]:
    return list(SECTORS)


@pytest.fixture
def month_ends() -> pd.DatetimeIndex:
    return pd.date_range("2000-01-31", periods=240, freq="ME")


@pytest.fixture
def sector_returns(month_ends, sectors) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    market = rng.normal(0.006, 0.04, len(month_ends))
    betas = np.linspace(0.6, 1.4, len(sectors))
    idio = rng.normal(0.0, 0.025, (len(month_ends), len(sectors)))
    return pd.DataFrame(market[:, None] * betas[None, :] + idio, index=month_ends, columns=sectors)


@pytest.fixture
def cov(sector_returns) -> pd.DataFrame:
    return sector_returns.cov()


@pytest.fixture
def benchmark(sectors) -> pd.Series:
    w = pd.Series([33, 13, 9, 10, 5, 3, 8, 2, 2, 2, 10], index=sectors, dtype=float)
    return w / w.sum()


@pytest.fixture
def benchmark_frame(benchmark, month_ends) -> pd.DataFrame:
    return pd.DataFrame(
        [benchmark.values] * len(month_ends), index=month_ends, columns=benchmark.index
    )


@pytest.fixture
def vintages() -> pd.DataFrame:
    """January CPI published Feb 12 (100.0), revised Mar 11 (100.3); February published Mar 11."""
    return pd.DataFrame(
        {
            "series_id": ["CPI", "CPI", "CPI"],
            "obs_date": pd.to_datetime(["2020-01-31", "2020-01-31", "2020-02-29"]),
            "realtime_start": pd.to_datetime(["2020-02-12", "2020-03-11", "2020-03-11"]),
            "value": [100.0, 100.3, 100.6],
        }
    )


@pytest.fixture
def panel(sector_returns, benchmark_frame) -> Panel:
    return Panel(vintages=EMPTY_VINTAGES, returns=sector_returns, benchmark_weights=benchmark_frame)
