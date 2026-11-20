"""FRED downloads into the CSV cache (needs network access and a free API key)."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pandas as pd

from sigtd.data.cache import read_fred_csv, write_fred_csv


def download(
    series_id: str, *, raw_dir: Path, api_key_env: str = "FRED_API_KEY", refresh: bool = False
) -> pd.Series:
    """Latest-vintage history of one series, cached as raw_dir/<id>.csv."""
    path = raw_dir / f"{series_id}.csv"
    if path.exists() and not refresh:
        return read_fred_csv(path)
    key = os.environ.get(api_key_env)
    if not key:
        raise RuntimeError(f"Set {api_key_env} (free key at fred.stlouisfed.org) to download data.")
    from fredapi import Fred

    fred = Fred(api_key=key)
    for attempt in range(3):
        try:
            s = fred.get_series(series_id).dropna()
            break
        except Exception:  # network hiccups: back off and retry
            if attempt == 2:
                raise
            time.sleep(2**attempt)
    write_fred_csv(s, path)
    return read_fred_csv(path)
