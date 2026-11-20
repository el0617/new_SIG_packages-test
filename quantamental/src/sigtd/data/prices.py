"""Monthly total returns for ETFs and sector indices."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TODO = "Phase 1 (M1): write prices"


def monthly_total_returns(
    tickers: list[str], start: str, *, cache_dir: Path, refresh: bool = False
) -> pd.DataFrame:
    """Month-end total returns (decimal) from adjusted closes; one column per ticker."""
    raise NotImplementedError(TODO)


def excess_returns(returns: pd.DataFrame, rf_annual_pct: pd.Series) -> pd.DataFrame:
    """Subtract the 3-month T-bill, converted to a monthly decimal rate."""
    raise NotImplementedError(TODO)
