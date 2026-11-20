"""Series registry, read from config.yaml."""

from __future__ import annotations

import pandas as pd

from sigtd.config import Config

REQUIRED = {"id", "source", "transform", "release_lag_days", "block"}


def load_registry(cfg: Config) -> pd.DataFrame:
    """One row per series, indexed by id."""
    df = pd.DataFrame([dict(s) for s in cfg["series"]])
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"series registry is missing fields: {sorted(missing)}")
    if df["id"].duplicated().any():
        raise ValueError("duplicate series id in registry")
    return df.set_index("id")
