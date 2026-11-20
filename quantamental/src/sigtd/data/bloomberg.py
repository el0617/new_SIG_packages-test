"""Import licensed Bloomberg CSV exports (files stay local; MANIFEST.md is committed)."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def manifest_files(folder: Path) -> set[str]:
    text = (folder / "MANIFEST.md").read_text() if (folder / "MANIFEST.md").exists() else ""
    return set(re.findall(r"^\|\s*([\w\-]+\.csv)\s*\|", text, flags=re.M))


def verify_manifest(folder: Path) -> None:
    """Every CSV in `folder` must have a row in MANIFEST.md."""
    present = {p.name for p in folder.glob("*.csv")}
    undocumented = present - manifest_files(folder)
    if undocumented:
        raise ValueError(f"Bloomberg exports missing from MANIFEST.md: {sorted(undocumented)}")


def import_exports(folder: Path) -> dict[str, pd.DataFrame]:
    """Parse each export into a month-end indexed frame, keyed by file stem. Empty if none."""
    if not folder.exists():
        return {}
    verify_manifest(folder)
    out = {}
    for p in sorted(folder.glob("*.csv")):
        df = pd.read_csv(p, index_col=0)
        df.index = pd.to_datetime(df.index) + pd.offsets.MonthEnd(0)
        out[p.stem] = df.apply(pd.to_numeric, errors="coerce").sort_index()
    return out
