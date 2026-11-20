"""The point-in-time Panel: the only object models receive.

Rule: every model has the signature run(panel, as_of, cfg) and may only use
panel.as_of(as_of), panel.returns_through(as_of) and panel.benchmark(as_of).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from sigtd.config import Config

TODO = "Phase 1 (M1): write the Panel"


@dataclass(frozen=True)
class Panel:
    vintages: pd.DataFrame  # long: series_id, obs_date, realtime_start, value
    returns: pd.DataFrame  # monthly total returns, month-end index, one column per sector key
    benchmark_weights: pd.DataFrame  # month-end index, one column per sector key, rows sum to 1

    def as_of(self, date: pd.Timestamp) -> pd.DataFrame:
        """Wide frame (index obs_date, columns series_id) of the latest value of every observation
        whose realtime_start <= date. Use ALFRED vintages where they exist and the registry's
        release_lag_days before that."""
        raise NotImplementedError(TODO)

    def returns_through(self, date: pd.Timestamp) -> pd.DataFrame:
        """Returns with index <= date."""
        raise NotImplementedError(TODO)

    def benchmark(self, date: pd.Timestamp) -> pd.Series:
        """Benchmark sector weights at the last month-end <= date."""
        raise NotImplementedError(TODO)


def build_panel(cfg: Config, refresh: bool = False) -> Panel:
    """Download or load every registry series, ETF/index returns and benchmark weights."""
    raise NotImplementedError(TODO)
