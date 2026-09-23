#!/usr/bin/env python3
"""RAAM historical backtest.

Uses the live engine's compute_signal() for every month-end, so it tests exactly what trades.
Execution mirrors the live bot: signal on the last trading day's close, fills at the next
session's open, held until the next rebalance open. Costs charged per side on turnover.

Scenarios
  A  real data only (IGOV exists)                     -> headline result
  B  IGOV spliced with BWX before Jan-2009            -> 2008 stress test

Variants are pre-registered (the paper's ambiguities + factor-contribution checks),
not a parameter search. Nothing here changes config/raam.json.

Usage: python backtest/backtest.py [--refresh] [--cost-bps 5]
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import raam  # noqa: E402

CACHE = ROOT / "data" / "cache" / "yahoo_raw.pkl"
OUT = ROOT / "backtest" / "results"
SYMS = ["VV", "IJH", "IJR", "EFA", "EEM", "RWR", "DBC", "VAW", "AGG", "TIP", "IGOV", "SHY", "SPY", "BWX"]
IS_END = dt.date(2019, 12, 31)          # in-sample / out-of-sample split
BREAKER_DD, BREAKER_DAY = -15.0, -5.0   # mirror config guardrails


# --------------------------------------------------------------------------- data
def load_raw(refresh: bool) -> pd.DataFrame:
    if refresh or not CACHE.exists():
        import yfinance as yf
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        df = yf.download(SYMS, start="2005-01-01", auto_adjust=True, progress=False,
                         group_by="ticker", threads=True)
        df.to_pickle(CACHE)
    return pd.read_pickle(CACHE)


def to_bars(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    bars = {}
    for s in SYMS:
        d = raw[s].rename(columns={"Open": "o", "High": "h", "Low": "l", "Close": "c", "Volume": "v"})
        d = d[["o", "h", "l", "c", "v"]].dropna(subset=["o", "h", "l", "c"])
        d.index = [ts.date() for ts in d.index]
        bars[s] = d.astype(float)
    return bars


def splice_igov(bars: dict) -> dict:
    """Scenario B: IGOV history extended backwards with BWX, scaled to be continuous."""
    igov, bwx = bars["IGOV"], bars["BWX"]
    first = igov.index[0]
    scale = igov.at[first, "c"] / bwx.at[first, "c"]
    early = bwx[bwx.index < first].copy()
    early[["o", "h", "l", "c"]] *= scale
    out = dict(bars)
    out["IGOV"] = pd.concat([early, igov])
    return out


# --------------------------------------------------------------------------- simulation
def month_ends(dates: list[dt.date]) -> list[dt.date]:
    s = pd.Series(dates, index=pd.to_datetime(dates))
    return list(s.groupby([s.index.year, s.index.month]).max())


def run(bars: dict, cfg: dict, cost_bps: float, no_trend: bool = False) -> dict:
    uni = cfg["universe"]
    assets = uni["risk_assets"] + [uni["cash"]]
    cal = list(bars["SPY"].index)
    idx = {d: i for i, d in enumerate(cal)}
    ends = month_ends(cal)
    hist_days = cfg["lookbacks"]["history_calendar_days"]

    orig_trend = raam.atr_trend_series
    if no_trend:
        raam.atr_trend_series = lambda b, *a, **k: pd.Series(0, index=b.index)
    signals = []
    try:
        for t in ends[:-1]:
            if idx[t] + 1 >= len(cal):
                break
            window = {s: bars[s][(bars[s].index <= t) &
                                  (bars[s].index >= t - dt.timedelta(days=hist_days))] for s in assets}
            try:
                sig = raam.compute_signal(window, cfg, t)
            except raam.Halt:
                continue                        # warm-up: not enough history yet
            signals.append((t, cal[idx[t] + 1], sig["targets"], sig["table"]))
    finally:
        raam.atr_trend_series = orig_trend

    opens = pd.DataFrame({s: bars[s]["o"] for s in assets + ["SPY"]}).reindex(cal)
    closes = pd.DataFrame({s: bars[s]["c"] for s in assets + ["SPY"]}).reindex(cal)

    periods, daily, prev_w = [], [], {s: 0.0 for s in assets}
    cost = cost_bps / 1e4
    for k, (t, entry, w, table) in enumerate(signals):
        exit_ = signals[k + 1][1] if k + 1 < len(signals) else cal[-1]
        last_is_close = k + 1 >= len(signals)
        p_in = opens.loc[entry]
        p_out = closes.loc[exit_] if last_is_close else opens.loc[exit_]
        rets = (p_out / p_in - 1.0)
        turnover = sum(abs(w.get(s, 0) - prev_w.get(s, 0)) for s in assets)
        gross = sum(w.get(s, 0) * rets[s] for s in assets)
        net = gross - cost * turnover
        ew = float(rets[assets].mean())
        periods.append({"signal_date": t, "entry": entry, "exit": exit_, "ret": net, "gross": gross,
                        "turnover": turnover, "spy": float(rets["SPY"]), "ew7twelve": ew,
                        "cash_w": w.get(uni["cash"], 0.0),
                        "held": {s: v for s, v in w.items() if v > 0},
                        "selected": [r["symbol"] for r in table if r["selected"]]})
        # daily path inside the holding period (for drawdown / circuit-breaker realism)
        seg = [d for d in cal[idx[entry]: idx[exit_] + (1 if last_is_close else 0)]]
        start_val = daily[-1][1] if daily else 1.0
        start_val *= (1 - cost * turnover)
        for d in seg:
            v = sum(w.get(s, 0) * closes.at[d, s] / p_in[s] for s in assets)
            daily.append((d, start_val * v))
        # drifted weights at exit
        port = 1 + gross
        prev_w = {s: w.get(s, 0) * (1 + rets[s]) / port for s in assets} if port else w
    return {"periods": pd.DataFrame(periods), "daily": pd.Series(dict(daily))}


# --------------------------------------------------------------------------- metrics
def stats(r: pd.Series, per_year: float = 12.0) -> dict:
    r = r.dropna()
    if r.empty:
        return {}
    eq = (1 + r).cumprod()
    years = len(r) / per_year
    cagr = eq.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan
    vol = r.std() * np.sqrt(per_year)
    dd = (eq / eq.cummax() - 1).min()
    return {"CAGR %": cagr * 100, "Vol %": vol * 100,
            "Sharpe": (r.mean() * per_year) / vol if vol else np.nan,
            "MaxDD % (monthly)": dd * 100, "Worst month %": r.min() * 100,
            "Best month %": r.max() * 100, "% months up": (r > 0).mean() * 100,
            "Total %": (eq.iloc[-1] - 1) * 100, "Months": len(r)}


def daily_risk(daily: pd.Series) -> dict:
    dd = daily / daily.cummax() - 1
    day = daily.pct_change()
    trips, peak, tripped = [], -np.inf, False
    for d, v in daily.items():
        peak = max(peak, v)
        ddv = (v / peak - 1) * 100
        dayv = day.get(d, 0) * 100
        if ddv <= BREAKER_DD or dayv <= BREAKER_DAY:
            if not tripped:
                trips.append((d.isoformat(), round(float(ddv), 1), round(float(dayv), 1)))
            tripped = True
        elif ddv > -5:
            tripped = False
    worst_i = dd.idxmin()
    return {"MaxDD % (daily)": dd.min() * 100, "MaxDD date": worst_i.isoformat(),
            "Worst day %": day.min() * 100, "breaker_trips": trips}


def fmt_table(rows: dict[str, dict], cols: list[str]) -> str:
    head = "| Variant | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols) + "\n"
    body = ""
    for name, st in rows.items():
        vals = []
        for c in cols:
            v = st.get(c)
            vals.append("" if v is None or (isinstance(v, float) and np.isnan(v))
                        else f"{v:.2f}" if isinstance(v, float) else str(v))
        body += f"| {name} | " + " | ".join(vals) + " |\n"
    return head + body


# --------------------------------------------------------------------------- variants
def variants(base: dict) -> dict[str, tuple[dict, bool]]:
    def v(**changes):
        c = copy.deepcopy(base)
        for path, val in changes.items():
            sect, key = path.split("__")
            c[sect][key] = val
        return c
    return {
        "Baseline (current config)": (base, False),
        "A3 lower band literal (+ATR)": (v(ambiguities__lower_band="hhv_low_plus_atr"), False),
        "A4 vol = Parkinson (H/L)": (v(ambiguities__vol_estimator="parkinson"), False),
        "A4 vol = Garman-Klass (OHLC)": (v(ambiguities__vol_estimator="garman_klass"), False),
        "A5 tiebreak literal (+M/x)": (v(ambiguities__tiebreak_sign=1), False),
        "A1 momentum-heavy 50/25/25": (v(ranking__w_momentum=0.5, ranking__w_volatility=0.25,
                                         ranking__w_correlation=0.25), False),
        "Check: momentum only 100/0/0": (v(ranking__w_momentum=1.0, ranking__w_volatility=0.0,
                                           ranking__w_correlation=0.0), False),
        "Check: no ATR trend filter": (base, True),
    }


# --------------------------------------------------------------------------- report
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="re-download Yahoo data")
    ap.add_argument("--cost-bps", type=float, default=5.0, help="cost per side, bps of turnover")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = raam.load_config()
    bars_a = to_bars(load_raw(args.refresh))
    bars_b = splice_igov(bars_a)

    results_a = {name: run(bars_a, c, args.cost_bps, nt) for name, (c, nt) in variants(cfg).items()}
    base_a = results_a["Baseline (current config)"]
    base_b = run(bars_b, cfg, args.cost_bps)

    pa = base_a["periods"]
    pb = base_b["periods"]
    start_a, end_a = pa["entry"].iloc[0], pa["exit"].iloc[-1]
    start_b = pb["entry"].iloc[0]

    def split(p, col):
        s = p.set_index("entry")[col]
        return s[s.index <= IS_END], s[s.index > IS_END]

    # headline: baseline vs benchmarks, full / in-sample / out-of-sample
    head = {}
    for label, col in (("RAAM baseline", "ret"), ("SPY", "spy"), ("Equal-weight 7Twelve", "ew7twelve")):
        full = pa.set_index("entry")[col]
        ins, oos = split(pa, col)
        head[f"{label} — full"] = stats(full)
        head[f"{label} — 2009-2019 (in-sample)"] = stats(ins)
        head[f"{label} — 2020-now (out-of-sample)"] = stats(oos)

    var_rows, var_oos = {}, {}
    for name, res in results_a.items():
        p = res["periods"]
        st = stats(p["ret"])
        st["Turnover/yr"] = p["turnover"].sum() / (len(p) / 12)
        st["Avg SHY %"] = p["cash_w"].mean() * 100
        var_rows[name] = st
        var_oos[name] = stats(split(p, "ret")[1])

    # 2008 stress (scenario B)
    crisis = pb[(pb["entry"] >= dt.date(2008, 6, 1)) & (pb["entry"] <= dt.date(2009, 6, 30))]
    crisis_rows = {
        "RAAM (BWX-spliced)": stats(crisis["ret"]), "SPY": stats(crisis["spy"]),
        "Equal-weight 7Twelve": stats(crisis["ew7twelve"])}
    for k in crisis_rows.values():
        k.pop("Sharpe", None)

    risk_a, risk_b = daily_risk(base_a["daily"]), daily_risk(base_b["daily"])
    spy_daily = bars_a["SPY"]["c"][bars_a["SPY"].index >= start_a]
    spy_dd = (spy_daily / spy_daily.cummax() - 1).min() * 100

    # calendar years
    cy = pa.copy()
    cy["year"] = [d.year for d in cy["entry"]]
    years = cy.groupby("year").agg(RAAM=("ret", lambda r: ((1 + r).prod() - 1) * 100),
                                   SPY=("spy", lambda r: ((1 + r).prod() - 1) * 100),
                                   EW7=("ew7twelve", lambda r: ((1 + r).prod() - 1) * 100),
                                   AvgSHY=("cash_w", lambda w: w.mean() * 100))
    # selection frequency
    held = pd.Series([s for h in pa["held"] for s in h]).value_counts()
    freq = (held / len(pa) * 100).round(1)

    # charts
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                               gridspec_kw={"height_ratios": [3, 1]})
        idx = pd.to_datetime(pa["exit"])
        for col, lab in (("ret", "RAAM baseline"), ("spy", "SPY"), ("ew7twelve", "Equal-weight 7Twelve")):
            eq = (1 + pa[col]).cumprod()
            ax[0].plot(idx, eq, label=lab)
            ax[1].plot(idx, (eq / eq.cummax() - 1) * 100, label=lab)
        ax[0].set_yscale("log"); ax[0].legend(); ax[0].set_title(f"Growth of $1 ({start_a} to {end_a}), log scale")
        ax[1].set_title("Drawdown %"); ax[1].grid(alpha=.3); ax[0].grid(alpha=.3)
        fig.tight_layout(); fig.savefig(OUT / "equity_curve.png", dpi=110)
    except Exception as e:  # charts are optional
        print("chart skipped:", e)

    pa.drop(columns=["held", "selected"]).to_csv(OUT / "monthly_baseline.csv", index=False)

    s_full = head["RAAM baseline — full"]
    report = f"""# RAAM Backtest Report

Generated {dt.date.today().isoformat()} by `backtest/backtest.py`. Costs: {args.cost_bps:g} bps per side on turnover.
Engine: the live `scripts/raam.py compute_signal()` with `config/raam.json`. Signal at the month-end close; fill at the next open.
Data: Yahoo Finance adjusted daily OHLC. Past results do not guarantee future results.

## 1. Headline: Scenario A, real data only ({start_a} → {end_a})
{fmt_table(head, ["CAGR %", "Vol %", "Sharpe", "MaxDD % (monthly)", "Worst month %", "% months up", "Months"])}
The Sharpe uses rf = 0.

**Daily-path risk (baseline):**
- Max drawdown **{risk_a['MaxDD % (daily)']:.1f}%**, reached on {risk_a['MaxDD date']}. SPY's max drawdown over the same span was {spy_dd:.1f}%.
- Worst single day **{risk_a['Worst day %']:.1f}%**.
- Circuit breaker (−15% from peak or −5% in one day) would have tripped **{len(risk_a['breaker_trips'])}** time(s): {risk_a['breaker_trips'] or 'never'}.

## 2. Pre-registered variants (Scenario A, full period)
{fmt_table(var_rows, ["CAGR %", "Vol %", "Sharpe", "MaxDD % (monthly)", "Worst month %", "Turnover/yr", "Avg SHY %"])}
### The same variants, out-of-sample only (2020 → now)
{fmt_table(var_oos, ["CAGR %", "Vol %", "Sharpe", "MaxDD % (monthly)", "Worst month %"])}
## 3. 2008 stress test: Scenario B, with IGOV spliced from BWX (entries Jun-2008 → Jun-2009)
Scenario B's first rebalance is {start_b}.
{fmt_table(crisis_rows, ["CAGR %", "Vol %", "MaxDD % (monthly)", "Worst month %", "Total %", "Months"])}
Scenario B daily max drawdown over its full history: **{risk_b['MaxDD % (daily)']:.1f}%** ({risk_b['MaxDD date']}). Breaker trips: {risk_b['breaker_trips'] or 'never'}.

## 4. Calendar years (Scenario A baseline)
| Year | RAAM % | SPY % | EW 7Twelve % | Avg SHY weight % |
|---|---|---|---|---|
""" + "".join(f"| {y} | {r.RAAM:.1f} | {r.SPY:.1f} | {r.EW7:.1f} | {r.AvgSHY:.0f} |\n" for y, r in years.iterrows()) + f"""
## 5. How often each ETF was held (% of months)
""" + " · ".join(f"{s} {v:g}%" for s, v in freq.items()) + """

![equity](equity_curve.png)
"""
    (OUT / "REPORT.md").write_text(report, encoding="utf-8")
    json.dump({"scenario_a": {"start": str(start_a), "end": str(end_a), "baseline": s_full,
                              "daily_risk": {k: v for k, v in risk_a.items()}},
               "variants_full": var_rows, "variants_oos": var_oos, "crisis_2008": crisis_rows},
              open(OUT / "summary.json", "w"), indent=2, default=str)
    sys.stdout.reconfigure(encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
