"""Which view moved the portfolio, and by how much (the slide that links analysts to weights)."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd


def leave_one_view_out(
    views: pd.DataFrame, run: Callable[[pd.DataFrame], pd.Series], aum_usd: float
) -> pd.DataFrame:
    """Re-run without each view. 'own_sector_pp' is how much this view moved its own sector;
    'total_moved_pp' is half the sum of absolute weight changes it caused across all sectors."""
    base = run(views)
    rows = []
    for i, v in views.iterrows():
        without = run(views.drop(index=i))
        delta = base - without
        moved = delta.abs().sum() / 2
        rows.append(
            {
                "view": f"{v['sector']} ({v['source']}: {v['owner']})",
                "q_pct": v["q"] * 100,
                "confidence_1to5": v["confidence_1to5"],
                "own_sector_pp": delta[v["sector"]] * 100,
                "total_moved_pp": moved * 100,
                "total_moved_usd": moved * aum_usd,
            }
        )
    return pd.DataFrame(rows)
