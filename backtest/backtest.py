#!/usr/bin/env python3
"""RAAM historical backtest.

Uses the live engine's compute_signal() for every month-end, so it tests exactly what trades.
Execution mirrors the live bot: signal on the last trading day's close, fills at the next
session's open, held until the next rebalance open. Costs charged per side on turnover.
The circuit breaker is simulated on the daily path: on a trip the portfolio moves to the cash
asset at that close and (reset = next_rebalance) re-enters at the next rebalance with the peak
re-based.

Scenarios
  A  real data only (IGOV exists)                     -> headline result
  B  IGOV spliced with BWX before Jan-2009            -> 2008 stress test

Variants are pre-registered (Tier 1 components, the paper's ambiguities, factor checks),
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
SYMS = ["VV", "IJH", "IJR", "EFA", "EEM", "RWR", "DBC", "VAW", "AGG", "TIP", "IGOV",
        "SHY", "BIL", "SPY", "BWX"]
IS_END = dt.date(2019, 12, 31)          # in-sample / out-of-sample split
LIVE = "**LIVE: Tier 1 + trend filter off (A)**"
EW_BENCH = ["VV", "IJH", "IJR", "EFA", "EEM", "RWR", "DBC", "VAW", "AGG", "TIP", "IGOV", "SHY"]


# --------------------------------------------------------------------------- data
def load_raw(refresh: bool) -> pd.DataFrame:
    need_download = refresh or not CACHE.exists()
    if not need_download:
        raw = pd.read_pickle(CACHE)
        need_download = any(s not in raw.columns.get_level_values(0) for s in SYMS)
    if need_download:
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


def breaker_from_cfg(cfg: dict) -> dict | None:
    g = cfg["guardrails"]
    if g.get("circuit_breaker_reset") != "next_rebalance":
        return None           # manual reset can't be simulated (needs a human decision)
    return {"dd": -float(g["circuit_breaker_drawdown_pct"]),
            "day": -float(g["circuit_breaker_daily_loss_pct"])}


def run(bars: dict, cfg: dict, cost_bps: float, no_trend: bool = False,
        breaker: dict | None = None) -> dict:
    uni = cfg["universe"]
    cash = uni["cash"]
    assets = uni["risk_assets"] + [cash]
    cal = list(bars["SPY"].index)
    idx = {d: i for i, d in enumerate(cal)}
    hist_days = cfg["lookbacks"]["history_calendar_days"]

    orig_trend = raam.atr_trend_series
    if no_trend:
        raam.atr_trend_series = lambda b, *a, **k: pd.Series(0, index=b.index)
    signals = []
    try:
        for t in month_ends(cal)[:-1]:
            if idx[t] + 1 >= len(cal):
                break
            window = {s: bars[s][(bars[s].index <= t) &
                                  (bars[s].index >= t - dt.timedelta(days=hist_days))] for s in assets}
            try:
                sig = raam.compute_signal(window, cfg, t)
            except raam.Halt:
                continue                        # warm-up: not enough history yet
            signals.append((t, cal[idx[t] + 1], sig["targets"]))
    finally:
        raam.atr_trend_series = orig_trend

    cols = sorted(set(assets + EW_BENCH + ["SPY"]))
    opens = pd.DataFrame({s: bars[s]["o"] for s in cols}).reindex(cal)
    closes = pd.DataFrame({s: bars[s]["c"] for s in cols}).reindex(cal)
    cost = cost_bps / 1e4

    periods, daily, trips = [], [], []
    prev_w = {s: 0.0 for s in assets}
    value, peak, prev_close_val = 1.0, 1.0, None
    for k, (t, entry, w) in enumerate(signals):
        last = k + 1 >= len(signals)
        exit_ = cal[-1] if last else signals[k + 1][1]
        turnover = sum(abs(w.get(s, 0) - prev_w.get(s, 0)) for s in assets)
        v0 = value * (1 - cost * turnover)
        p_in = opens.loc[entry]
        tripped_at, v_trip = None, None
        seg = cal[idx[entry]: idx[exit_] + (1 if last else 0)]
        for d in seg:
            if tripped_at is None:
                v = v0 * sum(w.get(s, 0) * closes.at[d, s] / p_in[s] for s in assets)
            else:
                v = v_trip * closes.at[d, cash] / closes.at[tripped_at, cash]
            if tripped_at is None:
                peak = max(peak, v)
                if breaker:
                    day_chg = (v / prev_close_val - 1) * 100 if prev_close_val else 0.0
                    dd = (v / peak - 1) * 100
                    if dd <= breaker["dd"] or day_chg <= breaker["day"]:
                        tripped_at = d
                        v = v * (1 - cost * 2 * (1 - w.get(cash, 0)))   # sell risk, buy cash
                        v_trip = v
                        trips.append((d.isoformat(), round(float(dd), 1), round(float(day_chg), 1)))
            daily.append((d, v))
            prev_close_val = v
        if last:
            value_exit = daily[-1][1]
        elif tripped_at is None:
            value_exit = v0 * sum(w.get(s, 0) * opens.at[exit_, s] / p_in[s] for s in assets)
        else:
            value_exit = v_trip * opens.at[exit_, cash] / closes.at[tripped_at, cash]
        p_out = closes.loc[exit_] if last else opens.loc[exit_]
        rets = p_out / p_in - 1.0
        periods.append({"signal_date": t, "entry": entry, "exit": exit_,
                        "ret": value_exit / value - 1, "turnover": turnover,
                        "spy": float(rets["SPY"]), "ew7twelve": float(rets[EW_BENCH].mean()),
                        "cash_w": w.get(cash, 0.0), "breaker": tripped_at is not None,
                        "held": {s: x for s, x in w.items() if x > 0}})
        if tripped_at is not None:
            prev_w = {s: (1.0 if s == cash else 0.0) for s in assets}
            peak = value_exit                  # auto re-entry re-bases the high-water mark
        else:
            port = sum(w.get(s, 0) * (1 + rets[s]) for s in assets)
            prev_w = {s: w.get(s, 0) * (1 + rets[s]) / port for s in assets} if port else w
        value = value_exit
    return {"periods": pd.DataFrame(periods), "daily": pd.Series(dict(daily)), "trips": trips}


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


def capture(r: pd.Series, bench: pd.Series) -> dict:
    """Downside/upside capture vs a benchmark (%): lower downside = better defence."""
    down, up = bench < 0, bench > 0
    return {"Down capture %": r[down].mean() / bench[down].mean() * 100 if down.any() else np.nan,
            "Up capture %": r[up].mean() / bench[up].mean() * 100 if up.any() else np.nan}


def daily_dd(daily: pd.Series) -> dict:
    dd = daily / daily.cummax() - 1
    return {"MaxDD % (daily)": dd.min() * 100, "MaxDD date": dd.idxmin().isoformat(),
            "Worst day %": daily.pct_change().min() * 100}


def fmt_table(rows: dict[str, dict], cols: list[str]) -> str:
    head = "| Variant | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols) + "\n"
    body = ""
    for name, st in rows.items():
        vals = []
        for c in cols:
            v = st.get(c)
            vals.append("" if v is None or (isinstance(v, float) and np.isnan(v))
                        else f"{v:.2f}" if isinstance(v, (float, np.floating)) else str(v))
        body += f"| {name} | " + " | ".join(vals) + " |\n"
    return head + body


# --------------------------------------------------------------------------- variants
def variants(live: dict) -> dict[str, tuple[dict, bool, dict | None]]:
    """name -> (config, no_trend, breaker). 'live' is config/raam.json (Tier 1)."""
    def v(base=live, **changes):
        c = copy.deepcopy(base)
        for path, val in changes.items():
            sect, key = path.split("__")
            c[sect][key] = val
        return c
    v1 = v(universe__cash="SHY", ranking__momentum_hurdle="zero", ranking__w_trend=1)
    brk = breaker_from_cfg(live)
    trend_on = v(ranking__w_trend=1)
    return {
        "v1 original (SHY, 0% hurdle, trend on, no breaker)": (v1, False, None),
        "Tier 1 (BIL + cash hurdle + breaker), trend on": (trend_on, False, brk),
        "Tier 1, trend on, breaker -15%": (trend_on, False, {"dd": -15.0, "day": -5.0}),
        LIVE: (live, False, brk),
        "Live + A3 lower band literal, trend on": (v(ranking__w_trend=1,
                                                      ambiguities__lower_band="hhv_low_plus_atr"), False, brk),
        "Live + momentum-heavy 50/25/25": (v(ranking__w_momentum=0.5, ranking__w_volatility=0.25,
                                             ranking__w_correlation=0.25), False, brk),
        "Live + SHY as cash": (v(universe__cash="SHY"), False, brk),
    }


V1 = "v1 original (SHY, 0% hurdle, trend on, no breaker)"


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

    res = {name: run(bars_a, c, args.cost_bps, nt, br) for name, (c, nt, br) in variants(cfg).items()}
    live, v1 = res[LIVE], res[V1]
    live_b = run(bars_b, cfg, args.cost_bps, breaker=breaker_from_cfg(cfg))
    v1_b = run(bars_b, variants(cfg)[V1][0], args.cost_bps)

    pa = live["periods"]
    start_a, end_a = pa["entry"].iloc[0], pa["exit"].iloc[-1]

    def split(p, col):
        s = p.set_index("entry")[col]
        return s[s.index <= IS_END], s[s.index > IS_END]

    head = {}
    for label, p, col in (("RAAM live (Tier 1 + A)", pa, "ret"), ("RAAM v1 original", v1["periods"], "ret"),
                          ("SPY", pa, "spy"), ("Equal-weight 7Twelve", pa, "ew7twelve")):
        s_all = p.set_index("entry")
        parts = {"full": s_all, "2009-2019": s_all[s_all.index <= IS_END],
                 "2020-now": s_all[s_all.index > IS_END]}
        for tag, part in parts.items():
            st = stats(part[col])
            if col != "spy":
                st.update(capture(part[col].values, part["spy"].values))
            head[f"{label} — {tag}"] = st

    var_rows, var_oos = {}, {}
    for name, r in res.items():
        p = r["periods"]
        st = stats(p["ret"])
        st.update(capture(p["ret"].values, p["spy"].values))
        st.update(daily_dd(r["daily"]))
        st["Turnover/yr"] = p["turnover"].sum() / (len(p) / 12)
        st["Avg cash %"] = p["cash_w"].mean() * 100
        st["Breaker trips"] = len(r["trips"])
        var_rows[name] = st
        oos = split(p, "ret")[1]
        so = stats(oos)
        so.update(capture(oos.values, split(p, "spy")[1].values))
        var_oos[name] = so

    crisis_rows = {}
    for label, p in (("RAAM live (Tier 1 + A)", live_b["periods"]), ("RAAM v1 original", v1_b["periods"])):
        c = p[(p["entry"] >= dt.date(2008, 6, 1)) & (p["entry"] <= dt.date(2009, 6, 30))]
        crisis_rows[label] = stats(c["ret"])
    c = live_b["periods"]
    c = c[(c["entry"] >= dt.date(2008, 6, 1)) & (c["entry"] <= dt.date(2009, 6, 30))]
    crisis_rows["SPY"] = stats(c["spy"])
    crisis_rows["Equal-weight 7Twelve"] = stats(c["ew7twelve"])

    def year_table(p):
        cy = p.copy()
        cy["year"] = [d.year for d in cy["entry"]]
        return cy.groupby("year").agg(R=("ret", lambda r: ((1 + r).prod() - 1) * 100),
                                      SPY=("spy", lambda r: ((1 + r).prod() - 1) * 100),
                                      EW7=("ew7twelve", lambda r: ((1 + r).prod() - 1) * 100),
                                      Cash=("cash_w", lambda w: w.mean() * 100))
    ylive, yv1 = year_table(pa), year_table(v1["periods"])
    held = pd.Series([s for h in pa["held"] for s in h]).value_counts()
    freq = (held / len(pa) * 100).round(1)
    spy_d = bars_a["SPY"]["c"][bars_a["SPY"].index >= start_a]
    spy_dd = (spy_d / spy_d.cummax() - 1).min() * 100

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
        x = pd.to_datetime(pa["exit"])
        for series, lab in ((pa["ret"], "RAAM live (Tier 1 + A)"), (v1["periods"]["ret"], "RAAM v1 original"),
                            (pa["spy"], "SPY"), (pa["ew7twelve"], "Equal-weight 7Twelve")):
            eq = (1 + series.values).cumprod()
            ax[0].plot(x, eq, label=lab)
            ax[1].plot(x, (eq / np.maximum.accumulate(eq) - 1) * 100, label=lab)
        ax[0].set_yscale("log"); ax[0].legend(); ax[0].grid(alpha=.3)
        ax[0].set_title(f"Growth of $1 ({start_a} to {end_a}), log scale")
        ax[1].set_title("Drawdown % (month-end)"); ax[1].grid(alpha=.3)
        fig.tight_layout(); fig.savefig(OUT / "equity_curve.png", dpi=110)
    except Exception as e:  # charts are optional
        print("chart skipped:", e)

    pa.drop(columns=["held"]).to_csv(OUT / "monthly_live.csv", index=False)
    old_csv = OUT / "monthly_baseline.csv"
    if old_csv.exists():
        old_csv.unlink()

    L = var_rows[LIVE]
    report = f"""# RAAM Backtest Report

Generated {dt.date.today().isoformat()} by `backtest/backtest.py`. Costs: {args.cost_bps:g} bps per side on turnover.
Engine: the live `scripts/raam.py compute_signal()` with `config/raam.json` (**Tier 1: BIL cash, cash-momentum hurdle, −20% breaker with auto re-entry; improvement A: trend term off**).
Signal at the month-end close, fill at the next open. The breaker is simulated on the daily path.
Data: Yahoo Finance adjusted daily OHLC. Past results do not guarantee future results.

## 1. Headline: Scenario A, real data only ({start_a} → {end_a})
{fmt_table(head, ["CAGR %", "Vol %", "Sharpe", "MaxDD % (monthly)", "Worst month %", "Down capture %", "Up capture %", "Months"])}
The Sharpe uses rf = 0.
- **Down capture:** the average RAAM return in SPY's down months, as a % of SPY's loss. Lower is better defence.
- **Up capture:** the same, for SPY's up months.

**Live config, daily path:**
- Max drawdown **{L['MaxDD % (daily)']:.1f}%** on {L['MaxDD date']}. SPY's max drawdown over the same span was {spy_dd:.1f}%.
- Worst day **{L['Worst day %']:.1f}%**.
- Breaker trips: **{len(live['trips'])}** {live['trips'] or ''}

## 2. Pre-registered variants (Scenario A, full period)
{fmt_table(var_rows, ["CAGR %", "Vol %", "Sharpe", "MaxDD % (daily)", "Down capture %", "Up capture %", "Turnover/yr", "Avg cash %", "Breaker trips"])}
### The same variants, out-of-sample only (2020 → now)
{fmt_table(var_oos, ["CAGR %", "Vol %", "Sharpe", "MaxDD % (monthly)", "Down capture %", "Up capture %"])}
## 3. 2008 stress test: Scenario B, with IGOV spliced from BWX (entries Jun-2008 → Jun-2009)
{fmt_table(crisis_rows, ["CAGR %", "Vol %", "MaxDD % (monthly)", "Worst month %", "Total %", "Months"])}
Scenario B live-config breaker trips: {live_b['trips'] or 'none'}.

## 4. Calendar years (Scenario A)
| Year | RAAM live % | RAAM v1 % | SPY % | EW 7Twelve % | Live avg cash % |
|---|---|---|---|---|---|
""" + "".join(f"| {y} | {r.R:.1f} | {yv1.loc[y].R:.1f} | {r.SPY:.1f} | {r.EW7:.1f} | {r.Cash:.0f} |\n"
              for y, r in ylive.iterrows()) + f"""
## 5. How often each ETF was held, live config (% of months)
""" + " · ".join(f"{s} {v:g}%" for s, v in freq.items()) + """

![equity](equity_curve.png)
"""
    (OUT / "REPORT.md").write_text(report, encoding="utf-8")
    json.dump({"scenario_a": {"start": str(start_a), "end": str(end_a)}, "headline": head,
               "variants_full": var_rows, "variants_oos": var_oos, "crisis_2008": crisis_rows,
               "live_trips": live["trips"]}, open(OUT / "summary.json", "w"), indent=2, default=str)
    sys.stdout.reconfigure(encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
