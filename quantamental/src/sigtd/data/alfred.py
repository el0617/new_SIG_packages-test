"""ALFRED vintages: what each number looked like on the day it was published.

When raw_dir/vintages/<id>.parquet exists, build_panel uses it instead of the release-lag rule.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


def download_vintages(
    series_id: str, *, raw_dir: Path, api_key_env: str = "FRED_API_KEY", refresh: bool = False
) -> pd.DataFrame:
    """Long frame: series_id, obs_date (month-end), realtime_start, value."""
    path = raw_dir / "vintages" / f"{series_id}.parquet"
    if path.exists() and not refresh:
        return pd.read_parquet(path)
    key = os.environ.get(api_key_env)
    if not key:
        raise RuntimeError(f"Set {api_key_env} to download ALFRED vintages.")
    from fredapi import Fred

    raw = Fred(api_key=key).get_series_all_releases(series_id)
    out = pd.DataFrame(
        {
            "series_id": series_id,
            "obs_date": pd.to_datetime(raw["date"]) + pd.offsets.MonthEnd(0),
            "realtime_start": pd.to_datetime(raw["realtime_start"]),
            "value": pd.to_numeric(raw["value"], errors="coerce"),
        }
    ).dropna()
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(path)
    return out


def load_vintages(series_id: str, raw_dir: Path) -> pd.DataFrame | None:
    path = raw_dir / "vintages" / f"{series_id}.parquet"
    return pd.read_parquet(path) if path.exists() else None
