#!/usr/bin/env python3
"""Extra README figures, saved to backtest/results/readme_metrics.json so every number traces to a file.

- Sharpe two ways: rf = 0 (as in the backtest report) and in excess of T-bills (BIL, open to open)
- Sortino (excess over T-bills / downside deviation below T-bills) and Calmar (CAGR / |worst month-end drawdown|)
- The same for Mar 2008 - Sep 2026 without Bitcoin (IGOV extended with BWX)
- Early vs late period (2015-19 vs 2020-26); not out-of-sample, the design used both
- Drawdown duration: longest time under water and the worst drawdown's peak -> trough -> recovery
- Turnover and the cost it implies; measured live slippage

Needs the Yahoo price cache (python backtest/backtest.py builds it). Usage: python docs/readme_metrics.py
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "backtest"), str(ROOT / "scripts")]
import backtest as bt  # noqa: E402
import raam  # noqa: E402

RES = ROOT / "backtest" / "results"
IS_END = dt.date(2019, 12, 31)


def rf_series(p: pd.DataFrame, bars: dict) -> np.ndarray:
    o, c = bars["BIL"]["o"], bars["BIL"]["c"]
    last = p["exit"].iloc[-1]
    return np.array([(c.loc[x] if x == last else o.loc[x]) / o.loc[e] - 1 for e, x in zip(p["entry"], p["exit"])])


def drawdown_stats(r: np.ndarray, dates: list) -> dict:
    eq = np.cumprod(1 + r)
    peak = np.maximum.accumulate(eq)
    dd = eq / peak - 1
    under, longest, run = dd < -1e-9, 0, 0
    for u in under:
        run = run + 1 if u else 0
        longest = max(longest, run)
    t = int(np.argmin(dd))
    p = int(np.argmax(eq[: t + 1])) if t else 0
    rec = next((i for i in range(t, len(eq)) if eq[i] >= eq[p]), None)
    return {"max_dd_pct": round(float(dd.min() * 100), 1), "peak": str(dates[p]), "trough": str(dates[t]),
            "months_peak_to_trough": t - p, "months_to_recover": None if rec is None else rec - t,
            "recovered": str(dates[rec]) if rec is not None else None, "longest_under_water_months": longest}


def stats(r: np.ndarray, rf: np.ndarray, dates: list, bench: np.ndarray | None = None) -> dict:
    yrs = len(r) / 12
    ex = r - rf
    out = {"cagr_pct": round(float((np.prod(1 + r) ** (1 / yrs) - 1) * 100), 1),
           "vol_pct": round(float(r.std(ddof=1) * np.sqrt(12) * 100), 1),
           "sharpe_rf0": round(float(r.mean() / r.std(ddof=1) * np.sqrt(12)), 2),
           "sharpe_vs_tbills": round(float(ex.mean() / ex.std(ddof=1) * np.sqrt(12)), 2),
           "sortino_vs_tbills": round(float(ex.mean() * 12 / (np.sqrt(np.mean(np.minimum(ex, 0) ** 2)) * np.sqrt(12))), 2),
           "months": len(r)}
    out.update(drawdown_stats(r, dates))
    out["calmar"] = round(out["cagr_pct"] / abs(out["max_dd_pct"]), 2) if out["max_dd_pct"] else None
    if bench is not None:
        down = bench < 0
        out["down_capture_vs_6040_pct"] = round(float(r[down].mean() / bench[down].mean() * 100), 0)
    return out


def attribution(y: np.ndarray, x: np.ndarray) -> dict:
    """OLS y = a + b*x on monthly excess returns: beta, annualised alpha and its t-statistic."""
    X = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    se = np.sqrt(resid @ resid / (len(y) - 2) * np.linalg.inv(X.T @ X)[0, 0])
    return {"beta": round(float(coef[1]), 2), "alpha_pct_per_year": round(float(coef[0] * 12 * 100), 1),
            "alpha_t": round(float(coef[0] / se), 1)}


def main() -> None:
    p = pd.read_csv(RES / "monthly_live.csv", parse_dates=["entry", "exit"])
    p["entry"], p["exit"] = p["entry"].dt.date, p["exit"].dt.date
    bars = bt.build_crypto(bt.to_bars(bt.load_raw(False)))
    rf = rf_series(p, bars)
    cfg = raam.load_config()
    noibit = bt.variants(cfg)[bt.NOIBIT][0]
    q = bt.run(bars, noibit, 5.0, breaker=bt.breaker_from_cfg(cfg))["periods"]
    q = q[q["entry"] >= p["entry"].iloc[0]].reset_index(drop=True)
    assert len(q) == len(p), (len(q), len(p))

    pv = bt.run(bars, bt.variants(cfg)[bt.PREV][0], 5.0, breaker=bt.breaker_from_cfg(cfg))["periods"]
    pv = pv[pv["entry"] >= p["entry"].iloc[0]].reset_index(drop=True)
    assert len(pv) == len(p), (len(pv), len(p))
    series = {"Core & Shield": p["ret"].values, "Core & Shield without Bitcoin": q["ret"].values,
              "Previous live (60/40 Core)": pv["ret"].values,
              "60/40": p["b6040"].values, "SPY": p["spy"].values}
    windows = {"full": slice(None), "2015-19": (p["entry"] <= IS_END).values,
               "2020-26": (p["entry"] > IS_END).values}
    out = {"window": [str(p["entry"].iloc[0]), str(p["exit"].iloc[-1])],
           "rf_tbills_cagr_pct": round(float((np.prod(1 + rf) ** (12 / len(rf)) - 1) * 100), 2), "stats": {}}
    for wname, m in windows.items():
        dates = list(p["exit"][m]) if not isinstance(m, slice) else list(p["exit"])
        out["stats"][wname] = {
            name: stats(r[m], rf[m], dates, None if name in ("60/40", "SPY") else p["b6040"].values[m])
            for name, r in series.items()}

    # long history without Bitcoin
    bars_b = bt.splice_igov(bars)
    b = bt.run(bars_b, noibit, 5.0, breaker=bt.breaker_from_cfg(cfg))["periods"]
    rf_b = rf_series(b, bars_b)
    prev_nb = bt.variants(noibit)[bt.PREV][0]
    pb = bt.run(bars_b, prev_nb, 5.0, breaker=bt.breaker_from_cfg(cfg))["periods"]
    pb = pb[pb["entry"] >= b["entry"].iloc[0]].reset_index(drop=True)
    assert len(pb) == len(b), (len(pb), len(b))
    dates_b = list(b["exit"])
    out["long_history_no_bitcoin"] = {
        "window": [str(b["entry"].iloc[0]), str(b["exit"].iloc[-1])],
        "stats": {"Core & Shield without Bitcoin": stats(b["ret"].values, rf_b, dates_b, b["b6040"].values),
                  "Previous live without Bitcoin": stats(pb["ret"].values, rf_b, dates_b, b["b6040"].values),
                  "60/40": stats(b["b6040"].values, rf_b, dates_b), "SPY": stats(b["spy"].values, rf_b, dates_b)}}

    turn = p["turnover"].iloc[1:]                            # first month is the initial purchase
    sig = json.load(open(ROOT / "memory" / "signals" / "2026-09.json", encoding="utf-8"))
    out["costs"] = {"two_sided_turnover_per_year": round(float(turn.mean() * 12), 2),
                    "one_sided_turnover_per_month_pct": round(float(turn.mean() / 2 * 100), 1),
                    "backtest_cost_bps_per_side": 5,
                    "implied_cost_pct_per_year": round(float(turn.mean() * 12 * 5 / 1e4 * 100), 2),
                    "live_slippage_first_rebalance": raam.slippage_summary(sig["executed"]["fills"])}
    # attribution vs 60/40 (excess over T-bills, monthly OLS) and calendar-year returns (by entry year)
    bench_ex = p["b6040"].values - rf
    out["attribution_vs_6040"] = {name: attribution(r - rf, bench_ex)
                                  for name, r in series.items() if name not in ("60/40", "SPY")}
    years = np.array([e.year for e in p["entry"]])
    out["calendar_years_pct"] = {
        name: {int(y): round(float((np.prod(1 + r[years == y]) - 1) * 100), 1) for y in sorted(set(years))}
        for name, r in series.items()}
    path = RES / "readme_metrics.json"
    path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
