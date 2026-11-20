"""Macro dashboard: every indicator's current percentile against 20 years, plus its 3m change."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sigtd.config import Config
from sigtd.data.panel import Panel

TODO = "Phase 1 (M1): write the dashboard"


def render_dashboard(panel: Panel, as_of: pd.Timestamp, cfg: Config) -> Path:
    raise NotImplementedError(TODO)
