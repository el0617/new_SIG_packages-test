"""Analyst view sheets and signal views -> Black-Litterman inputs (P, Q, confidence).

Every view is relative: "sector X beats the benchmark by Q per year", so P rows are e_X - w_b.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

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
VIEW_COLUMNS = ["sector", "q", "confidence_1to5", "source", "owner", "kill_trigger"]


def load_view_sheet(path: Path) -> pd.DataFrame:
    """Validate columns, directions and ranges; reject views without a kill trigger."""
    df = pd.read_csv(path)
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
    if df.empty:
        return df
    bad_dir = ~df["direction"].isin(["overweight", "underweight"])
    if bad_dir.any():
        raise ValueError(f"{path.name}: direction must be overweight/underweight")
    if not df["confidence_1to5"].between(1, 5).all():
        raise ValueError(f"{path.name}: confidence_1to5 must be 1-5")
    if df["kill_trigger"].fillna("").str.strip().eq("").any():
        raise ValueError(f"{path.name}: every view needs a kill trigger")
    sign = df["direction"].map({"overweight": 1, "underweight": -1})
    df["expected_rel_return_pp_12m"] = df["expected_rel_return_pp_12m"].abs() * sign
    return df


def signal_views(
    composite: pd.Series,
    sigma_annual: pd.Series,
    ic: float,
    confidence_1to5: int,
    threshold_z: float,
) -> pd.DataFrame:
    """Grinold's rule, alpha = IC x volatility x score, for sectors with |z| >= threshold."""
    if composite.empty or confidence_1to5 <= 0:
        return pd.DataFrame(columns=VIEW_COLUMNS)
    z = composite[composite.abs() >= threshold_z]
    rows = [
        {
            "sector": s,
            "q": ic * sigma_annual[s] * z[s],
            "confidence_1to5": confidence_1to5,
            "source": "signal",
            "owner": "engine (composite signal)",
            "kill_trigger": "scorecard verdict drops to none",
        }
        for s in z.index
    ]
    return pd.DataFrame(rows, columns=VIEW_COLUMNS)


def build_views(sheet: pd.DataFrame, signal_view_table: pd.DataFrame | None = None) -> pd.DataFrame:
    """Analyst views (pp -> decimal) plus any signal views, in one table."""
    analyst = pd.DataFrame(
        {
            "sector": sheet.get("sector", pd.Series(dtype=str)),
            "q": sheet.get("expected_rel_return_pp_12m", pd.Series(dtype=float)) / 100,
            "confidence_1to5": sheet.get("confidence_1to5", pd.Series(dtype=int)),
            "source": "analyst",
            "owner": sheet.get("owner", pd.Series(dtype=str)),
            "kill_trigger": sheet.get("kill_trigger", pd.Series(dtype=str)),
        }
    )
    parts = [p for p in (analyst, signal_view_table) if p is not None and not p.empty]
    if not parts:
        return pd.DataFrame(columns=VIEW_COLUMNS)
    return pd.concat(parts, ignore_index=True)[VIEW_COLUMNS]


def to_pq(views: pd.DataFrame, benchmark: pd.Series) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """P (views x sectors, relative to benchmark), Q (annual decimal), Idzorek confidence."""
    sectors = list(benchmark.index)
    rows = []
    for s in views["sector"]:
        row = -benchmark.copy()
        row[s] += 1.0
        rows.append(row.values)
    P = pd.DataFrame(rows, columns=sectors)
    Q = views["q"].astype(float).reset_index(drop=True)
    conf = views["confidence_1to5"].astype(int).map(CONFIDENCE_TO_IDZOREK).reset_index(drop=True)
    return P, Q, conf
