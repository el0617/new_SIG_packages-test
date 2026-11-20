"""Monthly total returns for ETFs, and the sector panel built from them."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sigtd.config import Config


def download_monthly_total_returns(tickers: list[str], start: str, path: Path) -> pd.DataFrame:
    """Month-end total returns from Yahoo adjusted closes (needs network); cached as CSV."""
    import yfinance as yf

    px = yf.download(tickers, start=start, auto_adjust=True, progress=False)["Close"]
    rets = px.resample("ME").last().pct_change(fill_method=None).iloc[1:]
    path.parent.mkdir(parents=True, exist_ok=True)
    rets.to_csv(path)
    return rets


def read_returns(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index) + pd.offsets.MonthEnd(0)
    return df.apply(pd.to_numeric, errors="coerce").sort_index()


def sector_returns(etf_returns: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """One column per sector key. Before an ETF existed, fall back along data.proxies."""
    proxies = cfg.get("data.proxies", {})
    out = {}
    for sector, ticker in cfg["mandate"]["instruments"].items():
        chain = list(proxies.get(sector, [ticker]))
        s = pd.Series(float("nan"), index=etf_returns.index)
        for t in chain:
            if t in etf_returns.columns:
                s = s.combine_first(etf_returns[t])
        out[sector] = s
    return pd.DataFrame(out)


def excess_returns(returns: pd.DataFrame, rf_annual_pct: pd.Series) -> pd.DataFrame:
    """Subtract the 3-month T-bill, converted to a monthly decimal rate."""
    rf = (rf_annual_pct / 1200).reindex(returns.index).ffill()
    return returns.sub(rf, axis=0)
