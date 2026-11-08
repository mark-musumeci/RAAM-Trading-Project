#!/usr/bin/env python3
"""Parameter sensitivity of the live rules on the headline data (2015-26 with Bitcoin). Research only.

Four two-setting grids around the live values, fixed before any result was seen, each cell a full backtest with
5 bps costs, next-open fills and the breaker. All cells are scored over the same months (the longest momentum
lookback sets the start). Writes backtest/results/param_sensitivity.json.
Usage: python backtest/param_sensitivity.py
"""
import copy
import json
import os
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import backtest as bt  # noqa: E402
import robustness as rb  # noqa: E402

_B, _C = {}, {}
LIVE = {"G1": (84, 10), "G2": (84, 5), "G3": (0.3333, 0.3333), "G4": (0.94, 10)}


def cells():
    out = []
    for m in (42, 63, 84, 105, 126, 147, 168):
        for s in range(6, 15):
            out.append(("G1", m, s))
    for c in (42, 63, 84, 105, 126, 168):
        for n in range(3, 9):
            out.append(("G2", c, n))
    for wm in (0.15, 0.25, 0.3333, 0.45, 0.55):
        for wv in (0.15, 0.25, 0.3333, 0.45, 0.55):
            if round(1 - wm - wv, 4) >= 0.1 - 1e-9:
                out.append(("G3", wm, wv))
    for lam in (0.90, 0.92, 0.94, 0.96, 0.98):
        for sm in (5, 10, 20):
            out.append(("G4", lam, sm))
    return out


def apply(cfg, grid, x, y):
    c = copy.deepcopy(cfg)
    if grid == "G1":
        c["lookbacks"]["momentum_days"] = x
        c["portfolio"]["core_trend"]["sma_months"] = y
    elif grid == "G2":
        c["lookbacks"]["correlation_days"] = x
        c["ranking"]["top_n"] = y
    elif grid == "G3":
        c["ranking"].update(w_momentum=x, w_volatility=y, w_correlation=round(1 - x - y, 4))
    elif grid == "G4":
        c["lookbacks"]["ewma_lambda"] = x
        c["lookbacks"]["vol_smooth_days"] = y
    return c


def job(spec):
    win, grid, x, y = spec
    if win not in _B:
        _B[win] = rb.bars_for(win)
        _C[win] = rb.configs()[win]["port"]
    bars, cfg = _B[win], apply(_C[win], grid, x, y)
    try:
        sig = bt.signals_for(bars, cfg)
        p = bt.simulate(bars, cfg, [(s[0], s[1], s[2]) for s in sig], 5.0, bt.breaker_from_cfg(cfg))["periods"]
    except Exception as e:  # noqa: BLE001
        return spec, {"error": repr(e)}
    return spec, {"entry": [str(e) for e in p["entry"]], "ret": p["ret"].tolist(), "b6040": p["b6040"].tolist(),
                  "spy": p["spy"].tolist()}


def metrics(r):
    r = np.asarray(r)
    eq = np.cumprod(1 + r)
    cagr = eq[-1] ** (12 / len(r)) - 1
    dd = (eq / np.maximum.accumulate(np.maximum(eq, 1.0)) - 1).min()
    return {"PF": float(r[r > 0].sum() / -r[r < 0].sum()), "CAGR": float(cagr * 100),
            "Sharpe": float(r.mean() / r.std(ddof=1) * np.sqrt(12)), "DD": float(dd * 100), "MAR": float(cagr / -dd)}


def main():
    specs = [(w, *c) for w in ("A",) for c in cells()]
    print(len(specs), "runs", flush=True)
    raw = {}
    with ProcessPoolExecutor(max(1, (os.cpu_count() or 2) - 1)) as ex:
        for i, (spec, res) in enumerate(ex.map(job, specs, chunksize=2)):
            raw[spec] = res
            if i % 40 == 0:
                print(i, flush=True)
    bad = {k: v for k, v in raw.items() if "error" in v}
    print("errors:", len(bad), list(bad.items())[:3], flush=True)
    out = {}
    for win in ("A",):
        rows = {k: v for k, v in raw.items() if k[0] == win and "error" not in v}
        first = max(v["entry"][0] for v in rows.values())
        out[win] = {"first_month": first, "cells": []}
        for (w, g, x, y), v in rows.items():
            i = v["entry"].index(first)
            m = metrics(v["ret"][i:])
            bench = metrics(v["b6040"][i:])
            spy = metrics(v["spy"][i:])
            out[win]["cells"].append({"grid": g, "x": x, "y": y, **m, "months": len(v["ret"][i:]),
                                      "b_Sharpe": bench["Sharpe"], "b_PF": bench["PF"], "b_DD": bench["DD"],
                                      "spy_Sharpe": spy["Sharpe"], "spy_PF": spy["PF"]})
    (HERE / "results" / "param_sensitivity.json").write_text(json.dumps(out), encoding="utf-8")
    print("done", flush=True)


if __name__ == "__main__":
    main()
