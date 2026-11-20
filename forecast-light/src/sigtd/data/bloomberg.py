"""Import licensed Bloomberg CSV exports (files stay local; MANIFEST.md is committed)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TODO = "Phase 1 (M1): write bloomberg import"


def verify_manifest(folder: Path) -> None:
    """Every CSV in `folder` must have a row in MANIFEST.md, and vice versa. Raise if not."""
    raise NotImplementedError(TODO)


def import_exports(folder: Path) -> dict[str, pd.DataFrame]:
    """Parse each export into a month-end indexed frame, keyed by file stem."""
    raise NotImplementedError(TODO)
