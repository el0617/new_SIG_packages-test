"""The point-in-time Panel: the only object models receive.

Rule: every model has the signature run(panel, as_of, cfg) and may only use
panel.as_of(as_of), panel.returns_through(as_of), panel.market_through(as_of),
panel.benchmark(as_of) and panel.extras (Bloomberg frames, already month-end indexed).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import pandas as pd

from sigtd.config import ROOT, Config
from sigtd.data import alfred, bloomberg, fred
from sigtd.data.cache import read_fred_csv, to_monthly
from sigtd.data.prices import download_monthly_total_returns, read_returns, sector_returns
from sigtd.data.registry import load_registry


@dataclass(frozen=True)
class Panel:
    vintages: pd.DataFrame  # long: series_id, obs_date, realtime_start, value
    returns: pd.DataFrame  # monthly total returns, month-end index, one column per sector key
    benchmark_weights: pd.DataFrame  # month-end index, one column per sector key
    market: pd.Series | None = None  # market (SPY) total returns
    extras: dict = field(default_factory=dict)  # Bloomberg frames
    _memo: dict = field(default_factory=dict, init=False, compare=False, repr=False)

    def as_of(self, date: pd.Timestamp) -> pd.DataFrame:
        """Wide frame (index obs_date, columns series_id): latest value of every observation
        whose realtime_start <= date."""
        date = pd.Timestamp(date)
        key = ("as_of", date)
        if key not in self._memo:
            v = self.vintages
            if v.empty:
                out = pd.DataFrame()
            else:
                v = v[v["realtime_start"] <= date]
                v = v.sort_values("realtime_start").drop_duplicates(
                    ["series_id", "obs_date"], keep="last"
                )
                out = v.pivot(index="obs_date", columns="series_id", values="value").sort_index()
            self._memo[key] = out
        return self._memo[key]

    def series(self, series_id: str, date: pd.Timestamp) -> pd.Series:
        snap = self.as_of(date)
        if series_id not in snap.columns:
            return pd.Series(dtype=float, name=series_id)
        return snap[series_id].dropna()

    def returns_through(self, date: pd.Timestamp) -> pd.DataFrame:
        return self.returns.loc[: pd.Timestamp(date)]

    def market_through(self, date: pd.Timestamp) -> pd.Series:
        """Market returns; the equal-weighted sector average when no market series is loaded."""
        r = self.returns_through(date)
        if self.market is None:
            return r.mean(axis=1)
        return self.market.loc[: pd.Timestamp(date)].reindex(r.index)

    def relative_returns_through(self, date: pd.Timestamp) -> pd.DataFrame:
        """Sector returns minus the market return."""
        return self.returns_through(date).sub(self.market_through(date), axis=0)

    def benchmark(self, date: pd.Timestamp) -> pd.Series:
        w = self.benchmark_weights.loc[: pd.Timestamp(date)].iloc[-1]
        return (w / w.sum()).rename("benchmark")

    def truncate(self, date: pd.Timestamp) -> Panel:
        """A copy that cannot see anything after `date` (used by the backtest)."""
        date = pd.Timestamp(date)
        v = self.vintages
        return Panel(
            vintages=v[v["realtime_start"] <= date] if not v.empty else v,
            returns=self.returns.loc[:date],
            benchmark_weights=self.benchmark_weights.loc[:date],
            market=None if self.market is None else self.market.loc[:date],
            extras={k: df.loc[:date] for k, df in self.extras.items()},
        )


def _lag_rule_vintages(s: pd.Series, series_id: str, lag_days: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "series_id": series_id,
            "obs_date": s.index,
            "realtime_start": s.index + pd.Timedelta(days=int(lag_days)),
            "value": s.values,
        }
    )


def build_panel(cfg: Config, refresh: bool = False) -> Panel:
    """Load every registry series, ETF returns and benchmark weights from the cache.

    refresh=True downloads FRED series and Yahoo prices first (needs network and FRED_API_KEY).
    """
    raw = ROOT / cfg.get("data.raw_dir")
    reg = load_registry(cfg)
    key_env = cfg.get("data.fred_api_key_env")
    prices_path = raw / cfg.get("data.prices_file")

    if refresh:
        for sid in reg.index:
            fred.download(sid, raw_dir=raw, api_key_env=key_env, refresh=True)
        tickers = sorted(
            {cfg.get("data.market")}
            | set(cfg["mandate"]["instruments"].values())
            | {t for chain in cfg.get("data.proxies", {}).values() for t in chain}
        )
        download_monthly_total_returns(tickers, cfg.get("sample.etf_start"), prices_path)

    frames, missing = [], []
    for sid, row in reg.iterrows():
        path = raw / f"{sid}.csv"
        if not path.exists():
            missing.append(sid)
            continue
        vint = alfred.load_vintages(sid, raw)
        if vint is None:
            monthly = to_monthly(read_fred_csv(path), row["agg"])
            vint = _lag_rule_vintages(monthly, sid, row["release_lag_days"])
        frames.append(vint)
    if missing:
        warnings.warn(f"series missing from {raw}: {missing}", stacklevel=2)
    if not frames:
        raise FileNotFoundError(
            f"No cached series in {raw}. Run `make import-fall-cache` or `make data` (FRED key)."
        )
    vintages = pd.concat(frames, ignore_index=True)

    etf = read_returns(prices_path)
    returns = sector_returns(etf, cfg).dropna(how="all")
    market = etf[cfg.get("data.market")].reindex(returns.index)

    extras = bloomberg.import_exports(ROOT / cfg.get("data.bloomberg_dir"))
    if "sector_weights" in extras:
        bw = extras.pop("sector_weights").reindex(columns=returns.columns)
    else:
        fallback = pd.Series(dict(cfg.get("data.benchmark_fallback")), dtype=float)
        bw = pd.DataFrame(
            [fallback.values] * len(returns), index=returns.index, columns=fallback.index
        )
    bw = bw.reindex(columns=returns.columns)
    return Panel(
        vintages=vintages, returns=returns, benchmark_weights=bw, market=market, extras=extras
    )
