#!/usr/bin/env python3
"""Does the RAAM ranking have real skill? Context only: nothing here changes the strategy.

Test 1 - random picks: keep every rule identical (Core, cash test, IBIT cap, breaker, costs, dates)
but let the Shield hold 5 *random* candidates each month, 1,000 times. If the real ranking beats
~95% of random portfolios, the price ranking is a genuine edge; if it sits mid-pack, the value comes
from the universe, the cash test and the Core. Two simpler rules are added to see which part matters:
  - momentum only: the 5 highest-momentum candidates (no volatility or correlation ranks)
  - no ranking: all 12 candidates, equal slots, each with the cash test
Test 2 - longer history without Bitcoin: 2008-2026 (IGOV extended with BWX), live rules minus IBIT.

Both windows are scored at portfolio level (Core & Shield) and for the Shield on its own.
Usage: python backtest/robustness.py [--n 1000] [--workers N]
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest as bt  # noqa: E402
raam = bt.raam

SEED = 20261014
WINDOWS = {"A": "2015–2026, live rules (with Bitcoin)", "B": "2008–2026, live rules without Bitcoin"}
_W: dict = {}


# ----------------------------------------------------------------------------- set-up
def configs() -> dict:
    live = raam.load_config()
    noibit = copy.deepcopy(live)
    noibit["universe"]["risk_assets"] = [s for s in live["universe"]["risk_assets"] if s != "IBIT"]
    noibit["portfolio"]["max_weight"] = {}

    def alone(c, cap):
        a = copy.deepcopy(c)
        a["portfolio"] = {"name": "Shield alone", "core": {}, "shield_weight": 1.0,
                          "max_weight": {"IBIT": cap} if cap else {}}
        return a
    return {"A": {"port": live, "shield": alone(live, 0.10)},
            "B": {"port": noibit, "shield": alone(noibit, None)}}


def bars_for(win: str) -> dict:
    base = bt.build_ibit(bt.to_bars(bt.load_raw(False)))
    return base if win == "A" else bt.splice_igov(base)


def compact(signals: list[tuple]) -> list[dict]:
    """What the random/simple rules need from each real signal."""
    out = []
    for t, entry, _targets, sig in signals:
        out.append({"t": t, "entry": entry, "hurdle": sig["momentum_hurdle"]["value_pct"],
                    "mom": {r["symbol"]: r["momentum_pct"] for r in sig["table"]},
                    "selected": [r["symbol"] for r in sig["table"] if r["selected"]],
                    "core": dict(sig["portfolio"]["core"])})        # this month's Core, after its trend filter
    return out


def _init(win: str, cfgs: dict, months: list[dict]):
    _W.update(win=win, bars=bars_for(win), cfgs=cfgs, months=months)


# ----------------------------------------------------------------------------- rules
def shield_weights(picks: list[str], m: dict, cash: str, n_slots: int) -> dict:
    w: dict[str, float] = {}
    for s in picks:
        dest = s if m["mom"][s] > m["hurdle"] else cash
        w[dest] = w.get(dest, 0.0) + 1.0 / n_slots
    return w


def targets_for(rule: str, m: dict, cfg: dict, rng=None) -> dict:
    cash = cfg["universe"]["cash"]
    risk = cfg["universe"]["risk_assets"]
    n = cfg["ranking"]["top_n"]
    if rule == "ranked":
        w = shield_weights(m["selected"], m, cash, n)
    elif rule == "momentum":
        picks = sorted(risk, key=lambda s: -m["mom"][s])[:n]
        w = shield_weights(picks, m, cash, n)
    elif rule == "all":
        w = shield_weights(list(risk), m, cash, len(risk))
    elif rule == "random":
        w = shield_weights(list(rng.choice(risk, n, replace=False)), m, cash, n)
    else:
        raise ValueError(rule)
    core = m["core"] if raam.portfolio_parts(cfg)[0] else {}       # Shield-alone configs have no Core
    t, _ = raam.apply_caps(raam.combine_targets(w, cfg, core), cfg)
    return t


def metrics(res: dict) -> dict:
    p = res["periods"]
    st = bt.stats(p["ret"])
    down = p["b6040"] < 0
    return {"CAGR": st["CAGR %"], "Sharpe": st["Sharpe"], "MaxDD month-end": st["MaxDD % (monthly)"],
            "MaxDD daily": bt.daily_dd(res["daily"])["MaxDD % (daily)"],
            "Down capture vs 60/40": p.loc[down, "ret"].mean() / p.loc[down, "b6040"].mean() * 100}


def job(spec: tuple) -> tuple:
    rule, level, seed = spec
    cfg = _W["cfgs"][level]
    rng = np.random.default_rng(seed) if seed is not None else None
    sigs = [(m["t"], m["entry"], targets_for(rule, m, cfg, rng)) for m in _W["months"]]
    res = bt.simulate(_W["bars"], cfg, sigs, 5.0, bt.breaker_from_cfg(cfg))
    return spec, metrics(res)


# ----------------------------------------------------------------------------- test 2 extras
def history_tables(bars: dict, cfg: dict, signals: list[tuple]) -> dict:
    res = bt.simulate(bars, cfg, signals, 5.0, bt.breaker_from_cfg(cfg))
    p = res["periods"].copy()
    p["year"] = [e.year for e in p["entry"]]
    periods = {"Full period": p, "2008–09 (crisis)": p[p.year <= 2009], "2010–14": p[(p.year >= 2010) & (p.year <= 2014)],
               "2015–19": p[(p.year >= 2015) & (p.year <= 2019)], "2020–26": p[p.year >= 2020]}
    sub = {}
    for lab, q in periods.items():
        for name, col in (("C&S (no Bitcoin)", "ret"), ("60/40", "b6040"), ("SPY", "spy")):
            s = bt.stats(q[col])
            sub[f"{lab} | {name}"] = {"CAGR %": s["CAGR %"], "Sharpe": s["Sharpe"],
                                      "MaxDD % (month-end)": s["MaxDD % (monthly)"], "Months": s["Months"]}
    years = p.groupby("year").agg(cs=("ret", lambda r: ((1 + r).prod() - 1) * 100),
                                  b=("b6040", lambda r: ((1 + r).prod() - 1) * 100),
                                  spy=("spy", lambda r: ((1 + r).prod() - 1) * 100),
                                  cash=("cash_w", lambda w: w.mean() * 100))
    r12 = (1 + p["ret"]).rolling(12).apply(np.prod, raw=True)
    b12 = (1 + p["b6040"]).rolling(12).apply(np.prod, raw=True)
    ok = r12.notna()
    return {"start": str(p["entry"].iloc[0]), "end": str(p["exit"].iloc[-1]), "sub": sub,
            "years": years.round(1).to_dict(orient="index"),
            "daily": bt.daily_dd(res["daily"]), "trips": res["trips"],
            "won12": float(((r12 - b12)[ok] > 0).mean() * 100),
            "smaller_dd_years": int(sum(1 for y, r in years.iterrows() if r.cs > r.b))}


# ----------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    args = ap.parse_args()
    cfgs = configs()
    out = {}
    for win in ("A", "B"):
        bars = bars_for(win)
        signals = bt.signals_for(bars, cfgs[win]["port"])
        months = compact(signals)
        # fidelity: the rebuilt "ranked" targets must equal the engine's own targets
        mism = sum(1 for (t, e, tg, _), m in zip(signals, months)
                   if any(abs(tg.get(s, 0) - v) > 1e-6
                          for s, v in targets_for("ranked", m, cfgs[win]["port"]).items()))
        specs = [(r, lvl, None) for r in ("ranked", "momentum", "all") for lvl in ("port", "shield")]
        specs += [("random", lvl, SEED + i) for i in range(args.n) for lvl in ("port", "shield")]
        print(f"window {win}: {len(months)} months, {mism} rebuild mismatches, {len(specs)} simulations ...",
              flush=True)
        with ProcessPoolExecutor(args.workers, initializer=_init, initargs=(win, cfgs[win], months)) as ex:
            res = dict(ex.map(job, specs, chunksize=8))
        w = {"months": len(months), "start": str(months[0]["entry"]), "rebuild_mismatches": mism}
        for lvl in ("port", "shield"):
            real = res[("ranked", lvl, None)]
            rnd = [res[("random", lvl, SEED + i)] for i in range(args.n)]
            dist = {k: np.array([r[k] for r in rnd]) for k in real}
            better = {"CAGR": True, "Sharpe": True, "MaxDD month-end": True, "MaxDD daily": True,
                      "Down capture vs 60/40": False}
            w[lvl] = {
                "real": real, "momentum": res[("momentum", lvl, None)], "all": res[("all", lvl, None)],
                "random_p5_p50_p95": {k: [float(np.percentile(v, q)) for q in (5, 50, 95)] for k, v in dist.items()},
                "beats_random_pct": {k: float(((dist[k] < real[k]) if better[k] else (dist[k] > real[k])).mean() * 100)
                                     for k in real},
                "random_sharpe": [round(float(v), 4) for v in dist["Sharpe"]],   # for the README histogram
            }
        if win == "B":
            w["history"] = history_tables(bars, cfgs["B"]["port"], signals)
        out[win] = w
    write_report(out, args.n)


def write_report(out: dict, n: int) -> None:
    f = lambda v, d=1: "n/a" if v is None else (f"−{abs(v):.{d}f}" if v < 0 else f"{v:.{d}f}")  # noqa: E731
    L = [f"# Robustness: does the ranking have skill?", "",
         f"Generated {dt.date.today().isoformat()} by `backtest/robustness.py`. Same engine, data, costs (5 bps), "
         "dates, cash test, IBIT cap and breaker as the live backtest. **Context only:** nothing here changes "
         "the strategy or the evaluation criteria.", ""]
    for win, w in out.items():
        L += [f"## Window {win}: {WINDOWS[win]} (from {w['start']}, {w['months']} months)", ""]
        for lvl, title in (("port", "Whole portfolio (Core & Shield)"), ("shield", "Shield on its own")):
            x = w[lvl]
            L += [f"### {title}", "",
                  "| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |",
                  "|---|---|---|---|---|---|"]
            for lab, r in (("**Live ranking** (momentum + volatility + correlation)", x["real"]),
                           ("Momentum only (top 5)", x["momentum"]), ("No ranking (all 12, equal slots)", x["all"])):
                L.append(f"| {lab} | {f(r['CAGR'])}% | {f(r['Sharpe'], 2)} | {f(r['MaxDD month-end'])}% | "
                         f"{f(r['MaxDD daily'])}% | {f(r['Down capture vs 60/40'], 0)}% |")
            q = x["random_p5_p50_p95"]
            L.append(f"| Random 5 picks ({n:,} runs): 5th / 50th / 95th percentile | "
                     + " | ".join(f"{f(q[k][0], 2 if k == 'Sharpe' else 1)} / {f(q[k][1], 2 if k == 'Sharpe' else 1)} / "
                                  f"{f(q[k][2], 2 if k == 'Sharpe' else 1)}"
                                  for k in ("CAGR", "Sharpe", "MaxDD month-end", "MaxDD daily", "Down capture vs 60/40")) + " |")
            b = x["beats_random_pct"]
            L += ["", f"**Live ranking beats {b['Sharpe']:.0f}% of random portfolios on Sharpe**, "
                      f"{b['CAGR']:.0f}% on return, {b['MaxDD daily']:.0f}% on worst daily drop and "
                      f"{b['Down capture vs 60/40']:.0f}% on down-market defence.", ""]
        if "history" in w:
            h = w["history"]
            L += [f"### Test 2: long history without Bitcoin ({h['start']} → {h['end']})", "",
                  "| Period | Strategy | Return / yr | Sharpe | Worst month-end drop | Months |", "|---|---|---|---|---|---|"]
            for k, v in h["sub"].items():
                per, name = k.split(" | ")
                L.append(f"| {per} | {name} | {f(v['CAGR %'])}% | {f(v['Sharpe'], 2)} | {f(v['MaxDD % (month-end)'])}% | {v['Months']} |")
            L += ["", f"Worst daily drop {f(h['daily']['MaxDD % (daily)'])}% on {h['daily']['MaxDD date']}; "
                      f"breaker trips: {h['trips'] or 'none'}. Beat 60/40 in {h['won12']:.0f}% of rolling 12-month "
                      f"windows; ahead of 60/40 in {h['smaller_dd_years']} of {len(h['years'])} calendar years.", "",
                  "| Year | C&S (no Bitcoin) | 60/40 | SPY | Avg cash |", "|---|---|---|---|---|"]
            for y, r in h["years"].items():
                L.append(f"| {y} | {f(r['cs'])}% | {f(r['b'])}% | {f(r['spy'])}% | {r['cash']:.0f}% |")
            L.append("")
    path = bt.OUT / "ROBUSTNESS.md"
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
    json.dump(out, open(bt.OUT / "robustness.json", "w", encoding="utf-8"), indent=1, default=str)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
