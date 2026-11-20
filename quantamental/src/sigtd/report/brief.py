"""Render the Friday model brief (one HTML page) from the pipeline's results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sigtd.config import Config

TODO = "Phase 7 (M8): write the brief renderer (jinja2, template in report/templates)"


def render_brief(context: dict, cfg: Config, as_of: pd.Timestamp) -> Path:
    """Write reports/brief_<as_of>.html and return its path."""
    raise NotImplementedError(TODO)
