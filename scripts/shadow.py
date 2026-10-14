#!/usr/bin/env python3
"""Shadow tracking: what pre-registered variants of the strategy would have done, without trading them.

At each month-end signal the variants in config/shadow.json are computed from the same data as the
live signal and saved once to memory/shadow/<month>.json (never recomputed later, so history can't
drift). Every run then rebuilds memory/SHADOW-LOG.md: each variant's monthly return from the open of
the first trading day to the open of the next month's first trading day (the current month is to
date), after a 5 bps-per-side cost on turnover. Context only: nothing here places orders or changes
the live strategy.

Usage: shadow.py [--date YYYY-MM-DD] [--force] [--dry-run]
  --force    re-record the latest month's variants even if already saved (missing months are always backfilled)
  --dry-run  compute and print, write nothing
Prints one JSON object: {"status", "recorded", "months", "since_start", "file"}.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import raam  # noqa: E402

SHADOW_CONFIG = raam.ROOT / "config" / "shadow.json"


def shadow_dir() -> pathlib.Path:
    return raam.MEMORY / "shadow"


def shadow_log() -> pathlib.Path:
    return raam.MEMORY / "SHADOW-LOG.md"


def load_shadow_config() -> dict:
    return json.loads(SHADOW_CONFIG.read_text(encoding="utf-8"))


# ----------------------------------------------------------------------------- variants
def variant_cfg(cfg: dict, spec: dict) -> dict:
    c = copy.deepcopy(cfg)
    rm = set(spec.get("remove", []))
    c["universe"]["risk_assets"] = [s for s in c["universe"]["risk_assets"] if s not in rm]
    pf = c.setdefault("portfolio", {})
    pf["max_weight"] = {k: v for k, v in (pf.get("max_weight") or {}).items() if k not in rm}
    if "core" in spec:
        pf["core"] = dict(spec["core"])
    return c


def variant_targets(bars: dict, cfg: dict, spec: dict, as_of: dt.date) -> dict:
    """Portfolio targets for one variant: Core + shield_weight x RAAM picks (+ optional satellite), capped."""
    c = variant_cfg(cfg, spec)
    sig = raam.compute_signal(bars, c, as_of)
    core, std_shield = raam.portfolio_parts(c)
    shield_w = float(spec.get("shield_weight", std_shield))
    t: dict[str, float] = {}
    for s, w in core.items():
        t[s] = t.get(s, 0.0) + w
    for s, w in sig["shield_targets"].items():
        if w > 0:
            t[s] = t.get(s, 0.0) + shield_w * w
    cash = c["universe"]["cash"]
    sat = spec.get("satellite")
    if sat:
        days = c["lookbacks"]["momentum_days"]
        closes = {s: bars[s][bars[s].index <= as_of]["c"] for s in (sat["symbol"], cash)}
        beats = raam.momentum(closes[sat["symbol"]], days) > raam.momentum(closes[cash], days)
        dest = sat["symbol"] if beats else cash
        t[dest] = t.get(dest, 0.0) + float(sat["weight"])
    t, _ = raam.apply_caps(t, c)
    t = {s: round(w, 6) for s, w in sorted(t.items()) if w > 1e-9}
    total = sum(t.values())
    if abs(total - 1.0) > 1e-4:
        raise raam.Halt(f"shadow variant weights sum to {total:.4f}")
    return {"targets": t, "shield_picks": [s for s, w in sig["shield_targets"].items() if w > 0]}


def all_symbols(cfg: dict, scfg: dict) -> list[str]:
    syms = list(raam.tradable_symbols(cfg))
    for spec in scfg["variants"].values():
        syms += list(spec.get("core", {}))
        if spec.get("satellite"):
            syms.append(spec["satellite"]["symbol"])
    for mix in (cfg.get("benchmark_mixes") or {}).values():
        syms += list(mix)
    return list(dict.fromkeys(syms))


def record_month(client, cfg: dict, scfg: dict, sig_file: pathlib.Path) -> dict:
    live = json.loads(sig_file.read_text(encoding="utf-8"))
    as_of = dt.date.fromisoformat(live["as_of"])
    bars, _ = raam.fetch_bars(client, all_symbols(cfg, scfg), as_of, cfg)
    bars = {s: b[b.index <= as_of] for s, b in bars.items()}
    out = {}
    for name, spec in scfg["variants"].items():
        if not {k for k in spec if not k.startswith("_")}:          # the live rules: use what was traded
            picks = [s for s, w in live.get("shield_targets", {}).items() if w > 0]
            out[name] = {"targets": {s: w for s, w in sorted(live["targets"].items()) if w > 0},
                         "shield_picks": picks, "source": "live signal file"}
        else:
            out[name] = variant_targets(bars, cfg, spec, as_of)
    return {"month": live["month"], "as_of": live["as_of"], "effective_month": live["effective_month"],
            "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "variants": out}


# ----------------------------------------------------------------------------- performance
def _first_trading_day(client, month: str) -> dt.date | None:
    info = raam.calendar_info(client, dt.date.fromisoformat(month + "-01"))
    return dt.date.fromisoformat(info["first_trading_day"]) if info["first_trading_day"] else None


def _hold(targets: dict, p0: pd.Series, p1: pd.Series) -> tuple[float, dict]:
    """Buy-and-hold return of `targets` from prices p0 to p1, and the drifted weights at p1."""
    grow = {s: w * float(p1[s]) / float(p0[s]) for s, w in targets.items()}
    total = sum(grow.values())
    return total - 1.0, {s: g / total for s, g in grow.items()}


def _turnover(new: dict, old: dict) -> float:
    return sum(abs(new.get(s, 0.0) - old.get(s, 0.0)) for s in set(new) | set(old))


def account_return(client, start: dt.date, end: dt.date) -> float | None:
    """Live account equity, close of `start` to close of `end` (after real costs)."""
    try:
        h = client.portfolio_history(start, end) or {}
    except Exception:  # noqa: BLE001 - the account column is optional context
        return None
    s = pd.Series(h.get("equity") or [], index=[dt.datetime.fromtimestamp(t, raam.ET).date()
                                                for t in (h.get("timestamp") or [])], dtype=float).dropna()
    s = s[(s > 0) & (s.index >= start) & (s.index <= end)]
    return float(s.iloc[-1] / s.iloc[0] - 1.0) if len(s) >= 2 else None


def performance(client, cfg: dict, scfg: dict, records: list[dict], d: dt.date) -> list[dict]:
    syms = all_symbols(cfg, scfg)
    bars, _ = raam.fetch_bars(client, syms, d, cfg)
    opens = pd.DataFrame({s: b["o"] for s, b in bars.items()}).sort_index()
    closes = pd.DataFrame({s: b["c"] for s, b in bars.items()}).sort_index()
    opens, closes = opens[opens.index <= d], closes[closes.index <= d]
    cost = float(scfg.get("cost_bps_per_side", 5)) / 1e4
    mixes = {k: v for k, v in (cfg.get("benchmark_mixes") or {}).items() if k == "60/40"}   # the headline
    names = list(scfg["variants"]) + list(mixes)
    prev_w = {n: {} for n in names}                          # drifted weights at the end of last month
    rows = []
    for rec in records:
        start = _first_trading_day(client, rec["effective_month"])
        if start is None or start > d or start not in opens.index:
            continue
        nxt = _first_trading_day(client, raam.next_month_key(start))
        complete = nxt is not None and nxt <= d and nxt in opens.index
        p0 = opens.loc[start]
        p1 = opens.loc[nxt] if complete else closes.iloc[-1]
        end_label = nxt if complete else closes.index[-1]
        row = {"month": rec["effective_month"], "start": start.isoformat(), "end": end_label.isoformat(),
               "complete": complete, "returns_pct": {}}
        for n in names:
            targets = rec["variants"][n]["targets"] if n in rec["variants"] else mixes.get(n)
            if targets is None:                               # variant added after this month: not tracked
                row["returns_pct"][n] = None
                continue
            r, drift = _hold(targets, p0, p1)
            r -= cost * _turnover(targets, prev_w[n])
            prev_w[n] = drift
            row["returns_pct"][n] = round(r * 100, 3)
        prev_close = raam.calendar_info(client, start)["prev_month_last_trading_day"]
        acct = account_return(client, dt.date.fromisoformat(prev_close),
                              (nxt - dt.timedelta(days=1)) if complete else d) if prev_close else None
        row["returns_pct"]["Live account"] = None if acct is None else round(acct * 100, 3)
        rows.append(row)
    return rows


def since_start(rows: list[dict]) -> dict:
    out = {}
    for n in (rows[0]["returns_pct"] if rows else {}):
        vals = [r["returns_pct"].get(n) for r in rows]
        if any(v is None for v in vals):
            out[n] = None
            continue
        g = 1.0
        for v in vals:
            g *= 1 + v / 100
        out[n] = round((g - 1) * 100, 3)
    return out


# ----------------------------------------------------------------------------- log
def _pct(v) -> str:
    if v is None:
        return "n/a"
    return f"{'−' if v < 0 else '+'}{abs(v):.2f}%"


def _holdings(t: dict) -> str:
    return ", ".join(f"{s} {w * 100:.0f}%" for s, w in sorted(t.items(), key=lambda x: (-x[1], x[0])))


def write_log(scfg: dict, records: list[dict], rows: list[dict], total: dict) -> None:
    cols = ["Live account"] + [n for n in (rows[0]["returns_pct"] if rows else {}) if n != "Live account"]
    lines = ["# Shadow Variants (tracked, never traded)", "",
             "Written by `scripts/shadow.py`; do not hand-edit. Variants are pre-registered in "
             "`config/shadow.json` (owner decision 2026-10-14). **Context only:** nothing here changes the live "
             "strategy; any change is an owner decision at a checkpoint (see `memory/EVALUATION-PLAN.md`).", "",
             f"Variant returns run from the open of the month's first trading day to the open of the next month's "
             f"first trading day, after {scfg.get('cost_bps_per_side', 5)} bps per side on turnover. The current "
             "month is to date. *Live account* is the real paper account (close-to-close equity, after real "
             "costs). Its gap to *Live model* is the replication check (evaluation B4).", "",
             "| Month | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
    for r in rows:
        label = r["month"] if r["complete"] else f"{r['month']} (to {r['end']})"
        lines.append(f"| {label} | " + " | ".join(_pct(r["returns_pct"].get(c)) for c in cols) + " |")
    if rows:
        lines.append("| **Since start** | " + " | ".join(f"**{_pct(total.get(c))}**" for c in cols) + " |")
    lines += ["", "## What each variant held"]
    for rec in reversed(records):
        lines += ["", f"### {rec['effective_month']} (signal {rec['as_of']}, recorded {rec['recorded_at'][:10]})",
                  "", "| Variant | Holdings |", "|---|---|"]
        for n, v in rec["variants"].items():
            lines.append(f"| {n} | {_holdings(v['targets'])} |")
    lines += ["", "## Variant definitions", ""]
    for n, spec in scfg["variants"].items():
        lines.append(f"- **{n}:** {spec.get('_why', '')}")
    shadow_log().write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------- main
def run(args) -> dict:
    cfg, scfg = raam.load_config(), load_shadow_config()
    client = raam.Alpaca()
    d = dt.date.fromisoformat(args.date) if args.date else raam.today_et()
    sig_files = sorted(p for p in raam.SIGNALS_DIR.glob("*.json")
                       if json.loads(p.read_text(encoding="utf-8"))["as_of"] <= d.isoformat()
                       and p.stem >= raam.prev_month_key(dt.date.fromisoformat(scfg["start_month"] + "-01")))
    if not sig_files:
        return {"status": "noop", "reason": "no live signal to shadow yet"}
    records = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(shadow_dir().glob("*.json"))}
    todo = [p for p in sig_files if p.stem not in records]          # backfills any month not yet recorded
    if args.force and sig_files[-1] not in todo:
        todo.append(sig_files[-1])
    for p in todo:
        records[p.stem] = record_month(client, cfg, scfg, p)
        if not args.dry_run:
            shadow_dir().mkdir(parents=True, exist_ok=True)
            (shadow_dir() / f"{p.stem}.json").write_text(json.dumps(records[p.stem], indent=2) + "\n",
                                                          encoding="utf-8")
    recorded = [p.stem for p in todo] or None
    recs = [records[k] for k in sorted(records)]
    rows = performance(client, cfg, scfg, recs, d)
    total = since_start(rows)
    if not args.dry_run:
        write_log(scfg, recs, rows, total)
    return {"status": "ok", "dry_run": args.dry_run, "recorded": recorded, "months": rows,
            "since_start": total, "file": str(shadow_log().relative_to(raam.ROOT))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    try:
        out, code = run(args), 0
    except raam.Halt as e:
        out, code = {"status": "halt", "reason": str(e)}, 2
    except Exception as e:  # noqa: BLE001 - report everything as JSON for Claude
        out, code = {"status": "error", "reason": f"{type(e).__name__}: {e}"}, 1
    print(json.dumps(out, indent=2, default=str))
    return code


if __name__ == "__main__":
    sys.exit(main())
