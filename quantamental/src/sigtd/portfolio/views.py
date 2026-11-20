"""Analyst view sheets and signal views -> Black-Litterman inputs (P, Q, confidence)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TODO = "Phase 5 (M6): write view handling"

# 1-5 analyst confidence -> Idzorek confidence (share of the way from prior to view)
CONFIDENCE_TO_IDZOREK = {1: 0.10, 2: 0.25, 3: 0.50, 4: 0.70, 5: 0.85}

COLUMNS = (
    "sector",
    "direction",
    "expected_rel_return_pp_12m",
    "confidence_1to5",
    "kill_trigger",
    "source",
    "owner",
)


def load_view_sheet(path: Path) -> pd.DataFrame:
    """Validate columns, sectors and ranges; reject views without a kill trigger."""
    raise NotImplementedError(TODO)


def build_views(
    sheet: pd.DataFrame, scores: dict[str, pd.Series], card: pd.DataFrame
) -> pd.DataFrame:
    """Analyst views plus signal views whose scorecard confidence > 0."""
    raise NotImplementedError(TODO)


def to_pq(views: pd.DataFrame, sectors: list[str]) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """P (views x sectors), Q (annual decimal), Idzorek confidence per view."""
    raise NotImplementedError(TODO)
