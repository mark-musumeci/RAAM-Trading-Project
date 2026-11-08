#!/usr/bin/env python3
"""Longer history with proxy funds (UPGRADE-PLAN 1.6): the live rules without Bitcoin from 1999, so the
2000–02 dot-com bust and the 2007–09 crisis are both in the test.

Each live fund is extended backwards with an older fund (or index) giving the same exposure, spliced the way
backtest.splice() does it (scaled to be continuous at the live fund's first day). Every proxy was checked to exist
on Yahoo with adjusted history; nothing is fabricated. Where no proxy exists for a year, that candidate is simply
left out of the ranking until data exists (the coverage table shows which), never filled in.

Mutual funds and indices have one price a day, so their open/high/low are rebuilt with replicate.nav_to_ohlc() so
the volatility factor equals the close-to-close estimate on those days.

T-bills: FRED could not be reached from this machine, so the cash asset before BIL/SGOV is a total-return index
built from Yahoo's ^IRX (13-week T-bill discount yield), accruing yield/360 per calendar day.

Writes backtest/results/proxies.json (read by evidence.py) and prints a summary.
Usage: python backtest/proxies.py
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import pathlib
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "docs"))
import backtest as bt  # noqa: E402

raam = bt.raam
CACHE = HERE.parent / "data" / "cache" / "yahoo_proxies.pkl"
OUT = HERE / "results" / "proxies.json"

# live symbol -> proxy chain, newest first (each older fund extends the one before it)
PROXY = {
    "QQQM": ["QQQ"],                 # Nasdaq-100 ETF, Mar 1999
    "VV": ["VFINX"],                 # Vanguard 500 Index (S&P 500)
    "IJH": ["VIMSX"],                # Vanguard Mid-Cap Index, May 1998
    "IJR": ["NAESX"],                # Vanguard Small-Cap Index
    "EFA": ["VTMGX"],                # Vanguard Developed Markets Index, Aug 1999
    "EEM": ["VEIEX"],                # Vanguard Emerging Markets Index
    "RWR": ["VGSIX"],                # Vanguard REIT Index
    "DBC": ["PCRIX"],                # PIMCO CommodityRealReturn, Jul 2002 (nothing earlier: DBC missing before)
    "VAW": ["FSDPX"],                # Fidelity Select Materials (an active sector fund: flagged in the report)
    "AGG": ["VBMFX"],                # Vanguard Total Bond Market Index
    "SCHP": ["TIP", "VIPSX"],        # iShares TIPS (Dec 2003), then Vanguard Inflation-Protected Securities (Jun 2000)
    "IGOV": ["BWX", "RPIBX"],        # SPDR Intl Treasury (Oct 2007), then T. Rowe Price International Bond
    "SGOV": ["BIL", "TBILL"],        # SPDR 1–3 Month T-Bill (May 2007), then the ^IRX total-return index
}
NAV_ONLY = {"VFINX", "VIMSX", "NAESX", "VTMGX", "VEIEX", "VGSIX", "PCRIX", "FSDPX", "VBMFX", "VIPSX", "RPIBX"}
LIVE = ["SPY", "QQQM", "VV", "IJH", "IJR", "EFA", "EEM", "RWR", "DBC", "VAW", "AGG", "SCHP", "IGOV", "BIL", "SGOV",
        "SHY"]
MIN_ROWS = 106


def nav_to_ohlc(d: pd.DataFrame) -> pd.DataFrame:
    """A series with only one price a day gets open = previous close and a high/low range chosen so that the
    Parkinson and Garman–Klass estimators both reduce exactly to the close-to-close estimator for that day."""
    c = d["c"]
    o = c.shift(1).fillna(c.iloc[0])
    a = (2 * np.sqrt(np.log(2)) - 1) / 2 * np.abs(np.log(c / o))
    out = d.copy()
    out["o"], out["h"], out["l"] = o, np.maximum(o, c) * np.exp(a), np.minimum(o, c) * np.exp(-a)
    return out


def load_raw(refresh: bool = False) -> pd.DataFrame:
    if CACHE.exists() and not refresh:
        return pd.read_pickle(CACHE)
    import yfinance as yf
    syms = sorted(set(LIVE) | {p for ch in PROXY.values() for p in ch if p != "TBILL"} | {"^IRX"})
    df = yf.download(syms, start="1997-01-01", auto_adjust=True, progress=False, group_by="ticker", threads=True)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(CACHE)
    return df


def tbill_index(irx: pd.DataFrame) -> pd.DataFrame:
    y = irx["c"] / 100.0
    days = pd.Series(pd.to_datetime(y.index), index=y.index).diff().dt.days.fillna(0).values
    growth = np.cumprod(1 + y.shift(1).fillna(y.iloc[0]).values * days / 360.0)
    c = pd.Series(100 * growth, index=y.index)
    d = pd.DataFrame({"o": c, "h": c, "l": c, "c": c, "v": 0.0})
    return nav_to_ohlc(d)


def build_bars() -> tuple[dict, dict]:
    raw = load_raw()
    b = {}
    for s in sorted(set(raw.columns.get_level_values(0))):
        d = raw[s].rename(columns={"Open": "o", "High": "h", "Low": "l", "Close": "c", "Volume": "v"})
        d = d[["o", "h", "l", "c", "v"]].dropna(subset=["o", "h", "l", "c"])
        d.index = [ts.date() for ts in d.index]
        b[s] = d.astype(float)
    b = {s: (nav_to_ohlc(d) if s in NAV_ONLY else d) for s, d in b.items()}
    b["TBILL"] = tbill_index(b.pop("^IRX"))
    starts = {}
    for live, chain in PROXY.items():
        src = [live] + chain
        starts[live] = {s: str(b[s].index[0]) for s in src if s in b}
        # splice from the oldest end: oldest proxy -> next -> ... -> live fund
        for older, newer in zip(reversed(src[1:]), list(reversed(src[:-1]))):
            b = bt.splice(b, newer, older)
    return b, starts


def coverage(b_raw_starts: dict, years: range) -> dict:
    out = {}
    for live, starts in b_raw_starts.items():
        live_start = dt.date.fromisoformat(starts[live])
        earliest = min(dt.date.fromisoformat(v) for v in starts.values())
        row = {}
        for y in years:
            d = dt.date(y, 12, 31)
            row[y] = "real" if live_start <= dt.date(y, 1, 1) else ("proxy" if earliest <= d else "missing")
        out[live] = row
    return out


def live_cfg() -> dict:
    cfg = raam.load_config()
    c = copy.deepcopy(cfg)
    c["universe"]["risk_assets"] = [s for s in cfg["universe"]["risk_assets"] if s != bt.CRYPTO]
    c["universe"]["sell_only"] = []
    c["portfolio"]["max_weight"] = {}
    return c


def signals(bars: dict, cfg: dict, first: dt.date) -> list[tuple]:
    cal = list(bars["SPY"].index)
    pos = {d: i for i, d in enumerate(cal)}
    hist = dt.timedelta(days=cfg["lookbacks"]["history_calendar_days"])
    out = []
    risk = cfg["universe"]["risk_assets"]
    need = [cfg["universe"]["cash"]] + list(cfg["portfolio"]["core"])
    for t in bt.month_ends(cal)[:-1]:
        if t < first or pos[t] + 1 >= len(cal):
            continue
        avail = [s for s in risk if (bars[s].index <= t).sum() >= MIN_ROWS]
        if len(avail) < cfg["ranking"]["top_n"]:
            continue
        c = copy.deepcopy(cfg)
        c["universe"]["risk_assets"] = avail
        window = {s: bars[s][(bars[s].index <= t) & (bars[s].index >= t - hist)] for s in avail + need}
        try:
            sig = raam.compute_signal(window, c, t)
        except raam.Halt:
            continue
        out.append((t, cal[pos[t] + 1], sig["targets"], sig, avail))
    return out


def sim_bars(bars: dict, syms: list[str]) -> dict:
    """Fill pre-inception gaps with the first price so zero-weight funds don't turn the portfolio sum into NaN.
    A fund is never held before it has data (signals() only ranks funds with history), so this changes nothing."""
    cal = list(bars["SPY"].index)
    out = dict(bars)
    for s in syms:
        out[s] = bars[s].reindex(cal).bfill().ffill()
    return out


def main() -> None:
    import readme_metrics as rm
    bars, starts = build_bars()
    cfg = live_cfg()
    sig = signals(bars, cfg, dt.date(1999, 6, 1))
    syms = sorted(set(raam.signal_symbols(cfg)) | set(bt.EW_BENCH) | {"SPY", "AGG", "BIL"})
    for s in bt.EW_BENCH:
        if s not in bars:
            bars[s] = bars["SPY"]                              # only used for an unused benchmark column
    sb = sim_bars(bars, syms)
    res = bt.simulate(sb, cfg, [(t, e, w) for t, e, w, *_ in sig], 5.0, bt.breaker_from_cfg(cfg))
    p = res["periods"].copy()
    p.index = [pd.Timestamp(e).strftime("%Y-%m") for e in p["entry"]]
    p[["entry", "exit", "ret", "spy", "b6040"]].to_csv(OUT.parent / "monthly_2000_no_bitcoin.csv", index=False)
    rf_px = sb["SGOV"]["o"]
    last = p["exit"].iloc[-1]
    rf = np.array([(sb["SGOV"]["c"].loc[x] if x == last else rf_px.loc[x]) / rf_px.loc[e] - 1
                   for e, x in zip(p["entry"], p["exit"])])
    dates = list(p["exit"])
    stats = {"Live rules (no Bitcoin)": rm.stats(p["ret"].values, rf, dates, p["b6040"].values),
             "60/40": rm.stats(p["b6040"].values, rf, dates), "SPY": rm.stats(p["spy"].values, rf, dates)}
    episodes = {"Dot-com bust (Mar 2000 – Sep 2002)": ("2000-03", "2002-09"),
                "Financial crisis (Nov 2007 – Feb 2009)": ("2007-11", "2009-02"),
                "2022 (Jan – Dec)": ("2022-01", "2022-12")}
    ep = {}
    for name, (a, b) in episodes.items():
        q = p[(p.index >= a) & (p.index <= b)]
        ep[name] = {}
        for lab, col in (("Live rules (no Bitcoin)", "ret"), ("60/40", "b6040"), ("SPY", "spy")):
            eq = pd.concat([pd.Series([1.0]), (1 + q[col]).cumprod().reset_index(drop=True)])   # from the start
            ep[name][lab] = {"total %": round(float(eq.iloc[-1] - 1) * 100, 1),
                             "worst drop %": round(float((eq / eq.cummax() - 1).min() * 100), 1)}
    core_off = [s[3]["core_trend"]["on"] for s in sig if s[3].get("core_trend")]
    by_year = {}
    for y in sorted({k[:4] for k in p.index}):
        q = p[p.index.str[:4] == y]
        by_year[y] = {lab: round(float((1 + q[col]).prod() - 1) * 100, 1)
                      for lab, col in (("Live rules (no Bitcoin)", "ret"), ("60/40", "b6040"), ("SPY", "spy"))}
    cov = coverage(starts, range(1999, 2027))
    n_avail = {pd.Timestamp(t).strftime("%Y-%m"): len(a) for t, _, _, _, a in sig}
    s0 = stats["Live rules (no Bitcoin)"]
    out = {"window": [p.index[0], p.index[-1]], "months": len(p), "proxy_map": PROXY, "proxy_first_dates": starts,
           "coverage": cov, "candidates_available_by_month": n_avail,
           "first_signal_candidates": sig[0][4], "stats": stats, "episodes": ep, "years": by_year,
           "core_trend_on_share_pct": round(100 * float(np.mean(core_off)), 0) if core_off else None,
           "breaker_trips": res["trips"],
           "notes": ["VAW's proxy FSDPX is an actively managed sector fund.",
                     "DBC has no proxy before PCRIX's Jul 2002 start; it joins the ranking once it has 106 sessions.",
                     "Cash before BIL (May 2007) is a total-return index built from the ^IRX 13-week T-bill yield.",
                     "QQQM before Oct 2020 is QQQ; before QQQ's Mar 1999 launch the Core cannot be computed, so the "
                     "test starts once QQQ has 10 month-end closes."],
           "trial": {"CAGR": s0["cagr_pct"], "Sharpe (rf=0)": s0["sharpe_rf0"], "Sharpe vs T-bills": s0["sharpe_vs_tbills"],
                     "worst month-end DD": s0["max_dd_pct"]}}
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "window": out["window"], "live": {k: s0[k] for k in ("cagr_pct", "sharpe_vs_tbills", "max_dd_pct", "calmar")},
                      "episodes": ep}, default=str))


if __name__ == "__main__":
    main()
