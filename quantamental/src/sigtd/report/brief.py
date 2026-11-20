"""Render the Friday model brief (one self-contained HTML page) from the pipeline's results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from sigtd.config import ROOT, Config
from sigtd.report import charts

TEMPLATES = Path(__file__).parent / "templates"


def _table(df: pd.DataFrame | None, digits: int = 2, index: bool = True) -> str:
    if df is None or len(df) == 0:
        return ""
    return df.to_html(float_format=lambda x: f"{x:,.{digits}f}", index=index, border=0, na_rep="")


def _pct(x: float) -> str:
    return "n/a" if pd.isna(x) else f"{x * 100:.1f}%"


def render_brief(
    context: dict, cfg: Config, as_of: pd.Timestamp, out_dir: Path | None = None
) -> Path:
    c = context
    aum = cfg.get("mandate.aum_usd")
    limit_pp = cfg.get("mandate.limits.active_weight_pp")
    w, b = c["weights"], c["benchmark"]
    active = w - b
    risk = c["risk"]

    weights = pd.DataFrame(
        {
            "ETF": pd.Series(dict(cfg["mandate"]["instruments"])),
            "benchmark %": b * 100,
            "proposed %": w * 100,
            "active pp": active * 100,
            "position vs benchmark $": active * aum,
        }
    ).sort_values("active pp", ascending=False)

    shares = c["regime_shares"]
    top = shares.idxmax()
    regime_sentence = (
        f"{shares[top] * 100:.0f}% of {len(c['regime_specs'])} regime specifications place the "
        f"latest month ({c['regime_month']:%B %Y}) in <strong>{top}</strong>."
    )
    p = c["p_recession"]
    recession_sentence = (
        f"Probability of a recession starting within 12 months: <strong>{_pct(p)}</strong>. "
        f"In risk-budget mode this sets a tracking-error target of {_pct(c['te_target_rb'])}."
    )
    sc = c["p_scores"]
    recession_scores = (
        f"Scored out of sample over {sc['months_scored']:.0f} months: AUC {sc['auc']:.2f} "
        f"(ranking), Brier skill {sc['brier_skill']:+.2f} vs always forecasting the base rate "
        "(calibration). Good ranking with weak calibration means: trust direction more than level."
    )

    card = c["scorecard"]
    tested = card[card["status"] == "tested"]
    n_pass = int((tested["verdict"] != "none").sum())
    scorecard_sentence = (
        f"{len(tested)} signal series tested, {n_pass} cleared the bar; "
        f"{int((card['status'] != 'tested').sum())} skipped for missing data. "
        + (
            "No signal view enters the portfolio, so weights move only through analyst views "
            "or the insurance rule."
            if n_pass == 0
            else "Qualifying signals enter as views at their mapped confidence."
        )
    )
    card_cols = [
        "status",
        "mean_ic",
        "t_stat",
        "power_threshold_ic",
        "p_holm",
        "verdict",
        "confidence",
    ]
    card_show = card.reindex(columns=[x for x in card_cols if x in card.columns])
    card_show["status"] = card_show["status"].str.slice(0, 48)

    risk_rows = {
        "Ex-ante tracking error (60m cov)": _pct(risk["te"]),
        **{
            f"Tracking error ({k[3:]} cov)": _pct(v)
            for k, v in risk.items()
            if k.startswith("te_") and k[3:].endswith("m")
        },
        "Beta to SPY (portfolio / benchmark)": f"{risk['beta']:.2f} / {risk['benchmark_beta']:.2f}",
        "3-month active VaR 95% (historical)": _pct(risk["var"]["hist_var"]),
        "3-month active CVaR 95% (historical)": _pct(risk["var"]["hist_cvar"]),
    }
    risk_table = _table(pd.DataFrame({"value": risk_rows}))

    mode_label = (
        "Black-Litterman (confident views present)"
        if c["mode"] == "black_litterman"
        else "Risk-budget fallback (no confident view: benchmark + insurance)"
    )
    biggest = active.abs().idxmax()
    lo, hi = risk["te_band"]
    te_note = (
        "below the usual range: a deliberately passive week"
        if risk["te"] < lo
        else "inside the usual range"
    )
    headline = (
        f"Largest tilt: {biggest} {active[biggest] * 100:+.1f} pp. Ex-ante tracking error "
        f"{_pct(risk['te'])} ({te_note} of {_pct(lo)}–{_pct(hi)})."
    )

    views = c.get("views")
    views_show = None
    if views is not None and len(views):
        views_show = views.assign(q_pct=views["q"] * 100).drop(columns="q")
    backtest = c.get("backtest")

    env = Environment(
        loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "j2"])
    )
    html = env.get_template("brief.html.j2").render(
        as_of=f"{as_of:%Y-%m-%d}",
        returns_through=f"{c['returns_through']:%B %Y}",
        aum=f"{aum:,.0f}",
        demo_views=c.get("demo_views", False),
        mode=c["mode"],
        mode_label=mode_label,
        headline=headline,
        chart_active=charts.active_weights(active * 100, limit_pp),
        weights_table=_table(weights),
        regime_sentence=Markup(regime_sentence),
        regime_table=_table((shares * 100).rename("share %").to_frame().T, 0),
        recession_sentence=Markup(recession_sentence),
        chart_recession=charts.recession_path(c["p_path"], c["usrec"]),
        recession_scores=recession_scores,
        scenario_table=_table((c["scenarios"] * 100).rename("prior %").to_frame().T, 0),
        analog_table=_table(c["analogs"].T, 1),
        scorecard_sentence=scorecard_sentence,
        scorecard_table=_table(card_show, 3),
        views_table=_table(views_show, 2, index=False),
        attribution_table=_table(c.get("attribution"), 2, index=False),
        risk_table=risk_table,
        chart_contrib=charts.bar(
            risk["contributions"] * 100, "Contribution to tracking error (Euler split)", "pp of TE"
        ),
        checks=risk["checks"],
        stress_table=_table(c["stress"], 2, index=False),
        shock_table=_table(c["factor_shocks"], 2, index=False),
        backtest_table=_table(backtest["summary"], 2) if backtest else "",
        chart_backtest=charts.cumulative(backtest["active"]) if backtest else "",
    )
    out_dir = out_dir or ROOT / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if c["mode"] == "black_litterman" else "_risk_budget"
    path = out_dir / f"brief_{as_of:%Y-%m-%d}{suffix}.html"
    path.write_text(html)
    return path
