"""ALFRED vintages: what each number looked like on the day it was published."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TODO = "Phase 1 (M1): write alfred.download_vintages"


def download_vintages(series_id: str, *, cache_dir: Path, refresh: bool = False) -> pd.DataFrame:
    """Long frame: series_id, obs_date, realtime_start, value (one row per release or revision).

    Hint: fredapi's get_series_all_releases returns exactly this shape.
    """
    raise NotImplementedError(TODO)
