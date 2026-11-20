"""Which view moved the portfolio, and by how much (the slide that links analysts to weights)."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

TODO = "Phase 5 (M6): write leave-one-view-out attribution"


def leave_one_view_out(
    views: pd.DataFrame, run: Callable[[pd.DataFrame], pd.Series]
) -> pd.DataFrame:
    """Re-run without each view; report the weight change per sector in pp and dollars."""
    raise NotImplementedError(TODO)
