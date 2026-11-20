"""FRED downloads with a Parquet cache.

Write: API key from the env var named in config (data.fred_api_key_env); three retries with
backoff; a staleness warning when the last observation is older than the series' usual lag.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TODO = "Phase 1 (M1): write fred.download (see docs/design_note.md)"


def download(series_id: str, *, cache_dir: Path, refresh: bool = False) -> pd.Series:
    """Full latest-vintage history of one series, cached as Parquet."""
    raise NotImplementedError(TODO)
