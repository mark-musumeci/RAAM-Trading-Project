#!/usr/bin/env python3
"""Stress tests for the live Core & Shield config. Context only: nothing here changes the strategy.

Reuses backtest.py (same data, same engine, same execution model) and asks how fragile the
headline result is:
  1. costs          5 / 10 / 25 / 50 bps per side
  2. neighbourhood  lookbacks, top_n, EWMA lambda, factor weights nudged around the live values
  3. fill delay     1 (live) / 2 / 3 / 5 trading days after the signal
  4. rolling 12 mo  every 12-month window vs 60/40
  5. Monte Carlo    block bootstrap of live monthly returns (paired with 60/40)
  6. shocks         synthetic price shocks worse than history, injected at several dates

Usage: python backtest/stress.py [--workers N] [--paths 5000]
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest as bt  # noqa: E402
raam = bt.raam

EQUITY = ["SPY", "QQQM", "VV", "IJH", "IJR", "EFA", "EEM", "RWR", "VAW"]   # every equity ETF the live rules can hold
BONDS = ["AGG", "TIP", "IGOV"]
SHOCK_DATES = ["2016-11-15", "2017-09-15", "2019-07-15", "2021-06-15", "2023-11-15", "2025-08-15"]
AFTER_DAYS = 63                     # trading days watched after a shock ends
SEED = 20260927

# scenario -> {symbol: total return over the shock}, length in trading days
SCENARIOS = {
    "Crash day (1987-style, −20% equities and Bitcoin in one day)":
        ({**{s: -0.20 for s in EQUITY}, "IBIT": -0.20}, 1),
    "Stocks and bonds fall together (equities −25%, bonds −15% over 6 months)":
        ({**{s: -0.25 for s in EQUITY}, **{s: -0.15 for s in BONDS}, "IBIT": -0.25}, 126),
    "Stagflation (equities −20%, AGG/IGOV −10%, TIP +3%, DBC +25% over 6 months)":
        ({**{s: -0.20 for s in EQUITY}, "AGG": -0.10, "IGOV": -0.10, "TIP": 0.03, "DBC": 0.25,
          "IBIT": -0.30}, 126),
}
BTC_CRASH = "Bitcoin −80% in a month while IBIT is held"

_BARS = None


def _bars():
    global _BARS
    if _BARS is None:
        _BARS = bt.build_ibit(bt.to_bars(bt.load_raw(False)))
    return _BARS


def shock(bars: dict, moves: dict, start: dt.date, days: int) -> dict:
    """Scale prices from `start` by a geometric ramp reaching (1 + move) after `days` sessions.
    The shift is permanent: prices afterwards follow their real path from the lower level."""
    cal = list(bars["SPY"].index)
    i0 = cal.index(start)
    ramp = pd.Series(1.0, index=cal)
    out = dict(bars)
    for sym, move in moves.items():
        f = ramp.copy()
        for k in range(len(cal) - i0):
            f.iloc[i0 + k] = (1 + move) ** (min(k + 1, days) / days)
        b = bars[sym].copy()
        fac = f.reindex(b.index).fillna(1.0).values
        b[["o", "h", "l", "c"]] = b[["o", "h", "l", "c"]].mul(fac, axis=0)
        out[sym] = b
    return out


def job(spec: dict) -> tuple[str, dict]:
    bars = _bars()
    if spec.get("shock"):
        moves, start, days = spec["shock"]
        bars = shock(bars, moves, start, days)
    cfg = spec["cfg"]
    r = bt.run(bars, cfg, spec.get("cost", 5.0), breaker=bt.breaker_from_cfg(cfg),
               delay=spec.get("delay", 1))
    out = {"periods": r["periods"], "daily": r["daily"], "trips": r["trips"]}
    if spec.get("shock"):
        out["b6040_daily"] = 0.6 * bars["SPY"]["c"] / bars["SPY"]["c"].iloc[0] + \
            0.4 * bars["AGG"]["c"] / bars["AGG"]["c"].iloc[0]
    return spec["key"], out


# --------------------------------------------------------------------------- helpers
def summarize(r: dict, start: dt.date) -> dict:
    p = r["periods"][r["periods"]["entry"] >= start]
    d = r["daily"][r["daily"].index >= start]
    st, b = bt.stats(p["ret"]), bt.stats(p["b6040"])
    return {"CAGR %": st["CAGR %"], "Sharpe": st["Sharpe"],
            "MaxDD % (daily)": bt.daily_dd(d / d.iloc[0])["MaxDD % (daily)"],
            "Sharpe − 60/40": st["Sharpe"] - b["Sharpe"], "CAGR − 60/40 pp": st["CAGR %"] - b["CAGR %"],
            "Breaker trips": len([t for t in r["trips"] if t[0] >= start.isoformat()])}


def max_dd(eq: np.ndarray) -> np.ndarray:
    return (eq / np.maximum.accumulate(eq, axis=-1) - 1).min(axis=-1)


def bootstrap(ret: np.ndarray, b64: np.ndarray, months: int, block: int, n: int, rng) -> dict:
    T = len(ret)
    nb = -(-months // block)
    starts = rng.integers(0, T, size=(n, nb))
    ix = ((starts[:, :, None] + np.arange(block)) % T).reshape(n, -1)[:, :months]
    r, b = ret[ix], b64[ix]
    er, eb = np.cumprod(1 + r, axis=1), np.cumprod(1 + b, axis=1)
    yrs = months / 12
    cagr_r, cagr_b = er[:, -1] ** (1 / yrs) - 1, eb[:, -1] ** (1 / yrs) - 1
    sh_r = r.mean(1) * 12 / (r.std(1, ddof=1) * np.sqrt(12))
    sh_b = b.mean(1) * 12 / (b.std(1, ddof=1) * np.sqrt(12))
    dd_r, dd_b = max_dd(er), max_dd(eb)
    return {"cagr": cagr_r, "cagr_b": cagr_b, "sharpe": sh_r, "sharpe_b": sh_b, "dd": dd_r, "dd_b": dd_b,
            "total": er[:, -1] - 1, "total_b": eb[:, -1] - 1}


def pct(a, q):
    return float(np.percentile(a, q))


def shock_eval(r: dict, base: dict, start: dt.date, days: int) -> dict:
    d = r["daily"]
    cal = list(d.index)
    i0 = cal.index(start)
    i1 = min(len(cal) - 1, i0 + days - 1 + AFTER_DAYS)
    v0 = d.iloc[i0 - 1]
    win = d.iloc[i0: i1 + 1]
    trough = win.min() / v0 - 1
    it = i0 + int(np.argmin(win.values))           # recovery is counted from the low point
    rec = next((k for k, v in enumerate(d.iloc[it:]) if v >= v0), None) if trough < 0 else 0
    b = r["b6040_daily"].reindex(cal)
    b_trough = b.iloc[i0: i1 + 1].min() / b.iloc[i0 - 1] - 1
    bd = base["daily"]                     # same window, no shock: isolates the shock's effect
    base_trough = bd.iloc[i0: i1 + 1].min() / bd.iloc[i0 - 1] - 1
    trips = [t for t in r["trips"] if cal[i0].isoformat() <= t[0] <= cal[i1].isoformat()]
    return {"date": start.isoformat(), "loss %": trough * 100, "no-shock loss %": base_trough * 100,
            "60/40 loss %": b_trough * 100, "breaker": bool(trips),
            "recovery days": rec, "trip": trips[0] if trips else None}


# --------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--paths", type=int, default=5000)
    args = ap.parse_args()
    cfg = raam.load_config()
    bars = _bars()
    cal = list(bars["SPY"].index)
    snap = lambda s: next(d for d in cal if d >= dt.date.fromisoformat(s))  # noqa: E731

    def v(**kw):
        c = copy.deepcopy(cfg)
        for path, val in kw.items():
            sect, key = path.split("__")
            c[sect][key] = val
        return c

    def weights(factor, delta):
        keys = ["w_momentum", "w_volatility", "w_correlation"]
        w = {k: cfg["ranking"][k] for k in keys}
        w[factor] += delta
        for k in keys:
            if k != factor:
                w[k] -= delta / 2
        return v(**{f"ranking__{k}": round(x, 4) for k, x in w.items()})

    specs = [{"key": "live", "cfg": cfg}]
    specs += [{"key": f"cost {c:g}", "cfg": cfg, "cost": c} for c in (10, 25, 50)]
    specs += [{"key": f"delay {d}", "cfg": cfg, "delay": d} for d in (2, 3, 5)]
    params = {}
    for lb in (63, 105, 126):
        params[f"Lookback {lb} days (live 84)"] = v(lookbacks__momentum_days=lb, lookbacks__correlation_days=lb)
    for n in (4, 6):
        params[f"Hold top {n} (live 5)"] = v(ranking__top_n=n)
    for lam in (0.92, 0.97):
        params[f"EWMA λ {lam} (live 0.94)"] = v(lookbacks__ewma_lambda=lam)
    for f, name in (("w_momentum", "Momentum"), ("w_volatility", "Volatility"), ("w_correlation", "Correlation")):
        for dlt in (0.10, -0.10):
            params[f"{name} weight {dlt * 100:+.0f} pp"] = weights(f, dlt)
    specs += [{"key": f"param {k}", "cfg": c} for k, c in params.items()]
    for name, (moves, days) in SCENARIOS.items():
        specs += [{"key": f"shock {name}|{d}", "cfg": cfg, "shock": (moves, snap(d), days)}
                  for d in SHOCK_DATES]

    print(f"running {len(specs)} backtests on {args.workers} workers ...", flush=True)
    with ProcessPoolExecutor(args.workers) as ex:
        res = dict(ex.map(job, specs))

    # Bitcoin crash: pick months in which the live run actually held IBIT
    live = res["live"]
    held = live["periods"][[("IBIT" in h) for h in live["periods"]["held"]]]
    picks = held.iloc[np.linspace(0, len(held) - 1, 6).round().astype(int)]
    btc = [{"key": f"shock {BTC_CRASH}|{e.isoformat()}", "cfg": cfg,
            "shock": ({"IBIT": -0.80}, cal[cal.index(e) + 5], 21)} for e in picks["entry"]]
    with ProcessPoolExecutor(args.workers) as ex:
        res.update(dict(ex.map(job, btc)))

    # ---- 1-3: costs, neighbourhood, delay (all on the live window)
    start = max(r["periods"]["entry"].iloc[0] for k, r in res.items() if not k.startswith("shock"))
    rows_cost = {f"{c:g} bps per side" + (" (live assumption)" if c == 5 else ""):
                 summarize(res["live" if c == 5 else f"cost {c:g}"], start) for c in (5, 10, 25, 50)}
    rows_delay = {f"{d} day{'s' if d > 1 else ''} after the signal" + (" (live)" if d == 1 else ""):
                  summarize(res["live" if d == 1 else f"delay {d}"], start) for d in (1, 2, 3, 5)}
    rows_param = {"**Live settings**": summarize(live, start)}
    rows_param.update({k: summarize(res[f"param {k}"], start) for k in params})
    sh = [r["Sharpe"] for k, r in rows_param.items() if k != "**Live settings**"]
    beat = sum(r["Sharpe − 60/40"] > 0 for k, r in rows_param.items() if k != "**Live settings**")

    # ---- 4: rolling 12-month windows
    p = live["periods"][live["periods"]["entry"] >= start].reset_index(drop=True)
    r12 = (1 + p["ret"]).rolling(12).apply(np.prod, raw=True) - 1
    b12 = (1 + p["b6040"]).rolling(12).apply(np.prod, raw=True) - 1
    ok = r12.notna()
    gap = (r12 - b12)[ok] * 100

    def win_dd(col):
        out = []
        for i in range(11, len(p)):
            eq = np.cumprod(1 + p[col].values[i - 11: i + 1])
            out.append(max_dd(np.concatenate([[1.0], eq])))
        return np.array(out)
    dd_r, dd_b = win_dd("ret"), win_dd("b6040")
    down = (b12[ok] < 0).values
    roll = {
        "windows": int(ok.sum()),
        "won %": float((gap > 0).mean() * 100),
        "gap median pp": float(gap.median()), "gap p10 pp": float(gap.quantile(.1)),
        "gap p90 pp": float(gap.quantile(.9)),
        "C&S worst 12m %": float(r12[ok].min() * 100), "C&S best 12m %": float(r12[ok].max() * 100),
        "60/40 worst 12m %": float(b12[ok].min() * 100), "60/40 best 12m %": float(b12[ok].max() * 100),
        "C&S negative 12m %": float((r12[ok] < 0).mean() * 100),
        "smaller DD than 60/40 %": float((dd_r > dd_b).mean() * 100),
        "60/40 down windows": int(down.sum()),
        "won when 60/40 down %": float((gap.values[down] > 0).mean() * 100) if down.any() else None,
        "won when 60/40 up %": float((gap.values[~down] > 0).mean() * 100) if (~down).any() else None,
    }

    # ---- 5: Monte Carlo (paired block bootstrap)
    rng = np.random.default_rng(SEED)
    ret, b64 = p["ret"].values, p["b6040"].values
    mc10 = bootstrap(ret, b64, 120, 6, args.paths, rng)
    mc1 = bootstrap(ret, b64, 12, 6, args.paths, rng)
    mc = {
        "10y CAGR % p5/p50/p95": [pct(mc10["cagr"], q) * 100 for q in (5, 50, 95)],
        "10y 60/40 CAGR % p5/p50/p95": [pct(mc10["cagr_b"], q) * 100 for q in (5, 50, 95)],
        "10y Sharpe p5/p50/p95": [pct(mc10["sharpe"], q) for q in (5, 50, 95)],
        "10y 60/40 Sharpe p5/p50/p95": [pct(mc10["sharpe_b"], q) for q in (5, 50, 95)],
        "10y max DD % (month-end) p50/p95/p99": [pct(mc10["dd"], q) * 100 for q in (50, 5, 1)],
        "10y 60/40 max DD % p50/p95/p99": [pct(mc10["dd_b"], q) * 100 for q in (50, 5, 1)],
        "P(10y DD worse than −11.1%)": float((mc10["dd"] < -0.111).mean() * 100),
        "P(10y DD worse than −14.1%)": float((mc10["dd"] < -0.141).mean() * 100),
        "P(10y DD worse than −20%, breaker level)": float((mc10["dd"] < -0.20).mean() * 100),
        "P(10y Sharpe above 60/40)": float((mc10["sharpe"] > mc10["sharpe_b"]).mean() * 100),
        "P(10y DD smaller than 60/40)": float((mc10["dd"] > mc10["dd_b"]).mean() * 100),
        "P(1y return below 60/40)": float((mc1["total"] < mc1["total_b"]).mean() * 100),
        "P(1y return negative)": float((mc1["total"] < 0).mean() * 100),
        "1y return % p5/p50/p95": [pct(mc1["total"], q) * 100 for q in (5, 50, 95)],
    }

    # ---- 6: shocks
    shocks = {}
    for name, (moves, days) in list(SCENARIOS.items()) + [(BTC_CRASH, ({"IBIT": -0.8}, 21))]:
        rows = [(k, r) for k, r in res.items() if k.startswith(f"shock {name}|")]
        evals = []
        for k, r in rows:
            spec_date = k.split("|")[1]
            if name == BTC_CRASH:
                s0 = cal[cal.index(dt.date.fromisoformat(spec_date)) + 5]
            else:
                s0 = snap(spec_date)
            evals.append(shock_eval(r, live, s0, days))
        shocks[name] = evals

    # ---- report
    def ftab(rows, cols):
        return bt.fmt_table(rows, cols)
    cols = ["CAGR %", "Sharpe", "MaxDD % (daily)", "CAGR − 60/40 pp", "Sharpe − 60/40", "Breaker trips"]
    L = rows_param["**Live settings**"]
    lines = [f"# Stress Tests: Core & Shield (live config)",
             "",
             f"Generated {dt.date.today().isoformat()} by `backtest/stress.py`. Same data, engine and execution "
             f"model as `backtest/backtest.py`; window {start} → {p['exit'].iloc[-1]}. "
             "**Context only: none of this changes the strategy, the config or the evaluation criteria.**",
             "",
             f"Live baseline: CAGR {L['CAGR %']:.1f}%, Sharpe {L['Sharpe']:.2f}, daily max DD {L['MaxDD % (daily)']:.1f}%.",
             "",
             "## 1. Trading costs",
             ftab(rows_cost, cols),
             "## 2. Settings neighbourhood (is the live setting a lucky peak?)",
             "Each row changes one setting and keeps the rest live. Factor weight rows move one factor by "
             "±10 pp and split the difference across the other two.",
             ftab(rows_param, cols),
             f"Across the {len(sh)} nudged settings: Sharpe ranges {min(sh):.2f} to {max(sh):.2f} "
             f"(live {L['Sharpe']:.2f}); {beat} of {len(sh)} still beat 60/40's Sharpe.",
             "",
             "## 3. Late fills",
             ftab(rows_delay, cols),
             "## 4. Rolling 12-month windows vs 60/40 (what a single year can look like)",
             f"- {roll['windows']} overlapping windows. Core & Shield returned more than 60/40 in "
             f"**{roll['won %']:.0f}%** of them.",
             f"- 12-month gap vs 60/40: median {roll['gap median pp']:+.1f} pp; 1 in 10 windows was "
             f"worse than {roll['gap p10 pp']:+.1f} pp, 1 in 10 better than {roll['gap p90 pp']:+.1f} pp.",
             f"- Worst 12 months: C&S {roll['C&S worst 12m %']:.1f}% vs 60/40 {roll['60/40 worst 12m %']:.1f}%. "
             f"Best: C&S {roll['C&S best 12m %']:.1f}% vs 60/40 {roll['60/40 best 12m %']:.1f}%.",
             f"- C&S had a negative 12 months in {roll['C&S negative 12m %']:.0f}% of windows.",
             f"- C&S had the smaller drawdown inside the window in **{roll['smaller DD than 60/40 %']:.0f}%** of windows.",
             f"- In the {roll['60/40 down windows']} windows where 60/40 lost money, C&S did better in "
             f"{roll['won when 60/40 down %'] if roll['won when 60/40 down %'] is not None else float('nan'):.0f}%; "
             f"when 60/40 rose, C&S did better in {roll['won when 60/40 up %']:.0f}%.",
             "",
             f"## 5. Monte Carlo ({args.paths:,} paths, 6-month blocks of live monthly returns, paired with 60/40)",
             "Month-end values, so drawdowns are shallower than the daily path (the backtest's daily worst "
             f"was {L['MaxDD % (daily)']:.1f}%). Resampling history can't create crises that never happened; "
             "section 6 covers that.",
             "",
             "| Measure | Core & Shield | 60/40 |",
             "|---|---|---|",
             "| 10-year CAGR, 5th / 50th / 95th percentile | " + " / ".join(f"{x:.1f}%" for x in mc["10y CAGR % p5/p50/p95"]) +
             " | " + " / ".join(f"{x:.1f}%" for x in mc["10y 60/40 CAGR % p5/p50/p95"]) + " |",
             "| 10-year Sharpe, 5th / 50th / 95th | " + " / ".join(f"{x:.2f}" for x in mc["10y Sharpe p5/p50/p95"]) +
             " | " + " / ".join(f"{x:.2f}" for x in mc["10y 60/40 Sharpe p5/p50/p95"]) + " |",
             "| 10-year max drawdown: typical / 1-in-20 / 1-in-100 | " +
             " / ".join(f"{x:.1f}%" for x in mc["10y max DD % (month-end) p50/p95/p99"]) +
             " | " + " / ".join(f"{x:.1f}%" for x in mc["10y 60/40 max DD % p50/p95/p99"]) + " |",
             "",
             f"- Chance over 10 years of a month-end drawdown worse than −11.1%: {mc['P(10y DD worse than −11.1%)']:.0f}%; "
             f"worse than −14.1%: {mc['P(10y DD worse than −14.1%)']:.0f}%; worse than −20%: {mc['P(10y DD worse than −20%, breaker level)']:.1f}%.",
             f"- Chance of a higher 10-year Sharpe than 60/40: **{mc['P(10y Sharpe above 60/40)']:.0f}%**; "
             f"of a smaller 10-year drawdown than 60/40: **{mc['P(10y DD smaller than 60/40)']:.0f}%**.",
             f"- Any single year: {mc['P(1y return below 60/40)']:.0f}% chance of trailing 60/40, "
             f"{mc['P(1y return negative)']:.0f}% chance of a loss. 1-year return 5th / 50th / 95th: "
             + " / ".join(f"{x:+.1f}%" for x in mc["1y return % p5/p50/p95"]) + ".",
             "",
             "## 6. Synthetic shocks worse than history",
             "Each shock is injected into the price data at several dates (a permanent level shift; prices "
             "then follow their real path) and the full model is rerun, so the model reacts as it would live. "
             f"Loss = worst point from the day before the shock to {AFTER_DAYS} trading days after it ends. "
             "'No-shock' is the same window without the shock. 60/40 is buy-and-hold from the day before.",
             ""]
    for name, evals in shocks.items():
        lines += [f"### {name}", "",
                  "| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | "
                  "Back to pre-shock value (trading days after the low) |",
                  "|---|---|---|---|---|---|---|"]
        for e in evals:
            lines.append(f"| {e['date']} | {e['loss %']:.1f}% | {e['no-shock loss %']:.1f}% | "
                         f"{e['loss %'] - e['no-shock loss %']:+.1f} pp | {e['60/40 loss %']:.1f}% | "
                         f"{'tripped ' + e['trip'][0] if e['breaker'] else 'no'} | "
                         f"{e['recovery days'] if e['recovery days'] is not None else 'not yet'} |")
        ls = [e["loss %"] for e in evals]
        bs = [e["60/40 loss %"] for e in evals]
        own = [e["loss %"] - e["no-shock loss %"] for e in evals]
        if name == BTC_CRASH:              # 60/40 holds no Bitcoin, so compare with no shock instead
            lines += ["", f"Average extra loss from the Bitcoin crash: {np.mean(own):+.1f} pp "
                      f"(worst {min(own):+.1f} pp). 60/40 isn't exposed, so it isn't a fair comparison here.", ""]
        else:
            lines += ["", f"Average loss: C&S {np.mean(ls):.1f}% vs 60/40 {np.mean(bs):.1f}% "
                      f"(C&S took {np.mean(ls) / np.mean(bs) * 100:.0f}% of 60/40's loss). "
                      f"Worst: C&S {min(ls):.1f}%, 60/40 {min(bs):.1f}%.", ""]
    report = "\n".join(lines) + "\n"
    bt.OUT.mkdir(parents=True, exist_ok=True)
    (bt.OUT / "STRESS.md").write_text(report, encoding="utf-8")
    json.dump({"window": [str(start), str(p["exit"].iloc[-1])], "costs": rows_cost, "delay": rows_delay,
               "params": rows_param, "rolling_12m": roll, "monte_carlo": mc, "shocks": shocks},
              open(bt.OUT / "stress.json", "w", encoding="utf-8"), indent=2, default=str)
    sys.stdout.reconfigure(encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
