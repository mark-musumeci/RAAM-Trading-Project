#!/usr/bin/env python3
"""Monthly one-page PDF performance report for the Core & Shield paper account.

Deterministic: every number and chart comes from Alpaca data and the repo's signal files.
Claude only supplies up to 3 commentary bullets via --notes-file.

Usage:
  report.py [--month YYYY-MM] [--date YYYY-MM-DD] [--force] [--metrics-only] [--notes-file F]

Without --month/--force it only runs on the last trading day of the month (else noop).
Prints one JSON object: {"status", "file", "metrics"}. Writes reports/YYYY-MM.pdf.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
import textwrap

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import raam  # noqa: E402

# Reference palette (validated: 3 series all-pairs, light surface). Text uses ink tokens.
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
SERIES = {"Core & Shield": "#2a78d6", "60/40": "#eb6834", "SPY": "#1baf7a"}
GOOD_TEXT, BAD_TEXT = "#006300", "#d03b3b"
STATUS = {"normal": ("#0ca30c", "Normal"), "unusual": ("#fab219", "Unusual"),
          "outside": ("#d03b3b", "Outside backtest range"), "na": (MUTED, "n/a")}


def reports_dir() -> pathlib.Path:
    return raam.ROOT / "reports"


def month_bounds(month: str) -> tuple[dt.date, dt.date]:
    y, m = map(int, month.split("-"))
    first = dt.date(y, m, 1)
    last = (first + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)
    return first, last


def inception_date() -> dt.date | None:
    """First executed rebalance; else the first health snapshot; else None."""
    dates = []
    for p in sorted(raam.SIGNALS_DIR.glob("*.json")):
        ex = json.loads(p.read_text(encoding="utf-8")).get("executed")
        if ex and ex.get("at"):
            dates.append(dt.date.fromisoformat(ex["at"][:10]))
    if dates:
        return min(dates)
    hist = raam.load_state().get("equity_history") or []
    return dt.date.fromisoformat(hist[0]["date"]) if hist else None


def equity_series(client, start: dt.date, end: dt.date) -> pd.Series:
    h = client.portfolio_history(start, end) or {}
    s = pd.Series(h.get("equity") or [], index=[
        dt.datetime.fromtimestamp(t, raam.ET).date() for t in (h.get("timestamp") or [])],
        dtype=float).dropna()
    s = s[s > 0]
    return s[~s.index.duplicated(keep="last")].sort_index()


def fmt_pct(x, signed=True, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{x:+.{nd}f}%" if signed else f"{x:.{nd}f}%"


# --------------------------------------------------------------------------- metrics
def build(client, cfg: dict, month: str, as_of: dt.date) -> tuple[dict, dict]:
    first, _ = month_bounds(month)
    info = raam.calendar_info(client, first)
    prev = info.get("prev_month_last_trading_day")
    start = dt.date.fromisoformat(prev) if prev else first - dt.timedelta(days=1)
    end = min(dt.date.fromisoformat(info["last_trading_day"]), as_of)
    inc = inception_date()
    chart_start = min(start, inc - dt.timedelta(days=1)) if inc else start

    eq = equity_series(client, chart_start, end)
    core, shield_w = raam.portfolio_parts(cfg)
    cash = cfg["universe"]["cash"]
    mixes = cfg.get("benchmark_mixes", {"60/40": {"SPY": 0.6, "AGG": 0.4}})

    held_path = raam.signal_path(raam.prev_month_key(first))
    held_sig = json.loads(held_path.read_text(encoding="utf-8")) if held_path.exists() else None
    held = {s: w for s, w in (held_sig or {}).get("targets", {}).items() if w > 0} \
        if held_sig and held_sig.get("executed") else {}
    next_path = raam.signal_path(raam.month_key(end))
    next_sig = json.loads(next_path.read_text(encoding="utf-8")) if next_path.exists() else None

    syms = list(dict.fromkeys(["SPY"] + [s for m in mixes.values() for s in m] + list(held)))
    days = (end - chart_start).days + 10
    bars, _ = raam.fetch_bars(client, syms, end,
                              {**cfg, "lookbacks": {**cfg["lookbacks"], "history_calendar_days": days}})
    closes = pd.DataFrame({s: bars[s]["c"] for s in syms if s in bars}).sort_index()
    closes = closes[(closes.index >= chart_start) & (closes.index <= end)].ffill()

    def index_of(weights: dict) -> pd.Series:
        r = sum(closes[s].pct_change().fillna(0) * w for s, w in weights.items())
        return (1 + r).cumprod()
    bench = {name: index_of(w) for name, w in mixes.items()}
    bench["SPY"] = index_of({"SPY": 1.0})

    def pr(series, a, b):
        v = raam._period_return(series, a, b)
        return None if v is None else round(v, 3)

    month_ret = pr(eq, start, end)
    b_month = {k: pr(v, start, end) for k, v in bench.items()}
    since = round((eq.iloc[-1] / eq.iloc[0] - 1) * 100, 3) if len(eq) >= 2 else None
    b_since = {k: pr(v, eq.index[0], end) if len(eq) >= 2 else None for k, v in bench.items()}
    max_dd = round(float((eq / eq.cummax() - 1).min() * 100), 3) if len(eq) >= 2 else None

    rows = []
    for s, w in sorted(held.items(), key=lambda kv: -kv[1]):
        c = core.get(s, 0.0)
        sleeve = "Core" if abs(w - c) < 1e-9 else ("Shield" if c == 0 else "Core + Shield")
        r = pr(closes[s], start, end) if s in closes else None
        rows.append({"symbol": s, "sleeve": sleeve, "weight_pct": round(w * 100, 2),
                     "return_pct": r, "contribution_pct": None if r is None else round(w * r, 3)})

    next_rows = []
    if next_sig:
        for s, w in sorted(next_sig["targets"].items(), key=lambda kv: -kv[1]):
            if w <= 0:
                continue
            c = core.get(s, 0.0)
            next_rows.append({"symbol": s, "core_pct": round(c * 100, 1),
                              "shield_pct": round((w - c) * 100, 1), "total_pct": round(w * 100, 1)})

    norms = cfg.get("report_norms", {})
    checks = []
    lo, hi = norms.get("month_return_pct", [-3, 3])
    xlo, xhi = norms.get("month_return_extreme_pct", [-5.7, 6.0])
    if month_ret is None:
        checks.append(("Monthly return", "n/a", "na", "no equity data for the month"))
    else:
        st = "normal" if lo <= month_ret <= hi else ("unusual" if xlo <= month_ret <= xhi else "outside")
        checks.append(("Monthly return", fmt_pct(month_ret), st,
                       f"87% of backtest months were {lo:+g}% to {hi:+g}%"))
    cash_pct = round(held.get(cash, 0.0) * 100, 1) if held else None
    cmax = norms.get("cash_pct_max", 50)
    checks.append(("Cash (BIL) held", "n/a" if cash_pct is None else f"{cash_pct:.0f}%",
                   "na" if cash_pct is None else ("normal" if cash_pct <= cmax else "outside"),
                   f"backtest range 0–{cmax}%"))
    dd_floor = norms.get("max_drawdown_pct", -14.6)
    checks.append(("Drawdown since inception", fmt_pct(max_dd, signed=False),
                   "na" if max_dd is None else ("normal" if max_dd > dd_floor else "outside"),
                   f"backtest worst {dd_floor}%"))
    b64 = b_month.get("60/40")
    share_norm = norms.get("down_capture_vs_6040_pct", 70)
    if b64 is not None and month_ret is not None and b64 < 0:
        share = round(month_ret / b64 * 100, 1)
        checks.append(("Share of 60/40's loss", f"{share:.0f}%",
                       "normal" if share <= share_norm else "unusual",
                       f"backtest norm about {share_norm}%"))
    else:
        checks.append(("Share of 60/40's loss", "n/a", "na", "60/40 did not fall this month"))

    metrics = {
        "portfolio": (cfg.get("portfolio") or {}).get("name", "RAAM"),
        "month": month, "period": [start.isoformat(), end.isoformat()],
        "as_of": end.isoformat(), "inception": inc.isoformat() if inc else None,
        "equity_end": round(float(eq.iloc[-1]), 2) if len(eq) else None,
        "month_return_pct": month_ret, "benchmarks_month_pct": b_month,
        "vs_6040_month_pct": None if month_ret is None or b64 is None else round(month_ret - b64, 3),
        "since_inception_pct": since, "benchmarks_since_inception_pct": b_since,
        "max_drawdown_pct": max_dd, "cash_held_pct": cash_pct,
        "holdings": rows, "next_allocation": next_rows,
        "next_month": next_sig["effective_month"] if next_sig else None,
        "checks": [{"check": c[0], "value": c[1], "status": c[2], "reference": c[3]} for c in checks],
    }
    series = {"equity": eq, "bench": bench}
    return metrics, series


# --------------------------------------------------------------------------- rendering
def _style_axes(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=7, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def _table(ax, header, rows, col_w, aligns):
    ax.axis("off")
    if not rows:
        ax.text(0, 0.9, "Nothing to show yet.", color=MUTED, fontsize=8, va="top",
                transform=ax.transAxes)
        return
    t = ax.table(cellText=rows, colLabels=header, colWidths=col_w, loc="upper left",
                 cellLoc="left", edges="horizontal")
    t.auto_set_font_size(False)
    t.set_fontsize(7.5)
    t.scale(1, 1.25)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_linewidth(0.6)
        cell.set_facecolor(SURFACE)
        cell.get_text().set_color(INK2 if r == 0 else INK)
        cell.get_text().set_ha(aligns[c])
        if r == 0:
            cell.get_text().set_fontweight("bold")


def render(metrics: dict, series: dict, notes: list[str], path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=SURFACE)
    m_label = dt.date.fromisoformat(metrics["month"] + "-01").strftime("%B %Y")

    # header
    fig.text(0.05, 0.965, f"{metrics['portfolio']} — Monthly Report — {m_label}",
             fontsize=15, fontweight="bold", color=INK)
    fig.text(0.05, 0.947, f"Alpaca paper account · as of {metrics['as_of']} close · "
             f"inception {metrics['inception'] or 'not yet traded'} · "
             "Core 30% SPY + 20% AGG · Shield 50% RAAM", fontsize=8, color=INK2)

    # KPI tiles (2 rows x 3)
    b = metrics["benchmarks_month_pct"]
    bs = metrics["benchmarks_since_inception_pct"]
    diff = metrics["vs_6040_month_pct"]
    eqv = metrics["equity_end"]
    tiles = [
        ("Month return", fmt_pct(metrics["month_return_pct"]), f"60/40 {fmt_pct(b.get('60/40'))}", None),
        ("Versus 60/40 this month", "n/a" if diff is None else f"{diff:+.2f} pp",
         "percentage points (pp)", diff),
        ("Equity", "n/a" if eqv is None else f"${eqv:,.0f}", "paper account", None),
        ("Since inception", fmt_pct(metrics["since_inception_pct"]),
         f"60/40 {fmt_pct(bs.get('60/40'))} · SPY {fmt_pct(bs.get('SPY'))}", None),
        ("Max drawdown since inception", fmt_pct(metrics["max_drawdown_pct"], signed=False),
         "backtest worst −14.6%", None),
        ("Cash (BIL) held this month", "n/a" if metrics["cash_held_pct"] is None
         else f"{metrics['cash_held_pct']:.0f}%", "of the whole portfolio", None),
    ]
    for i, (label, value, sub, delta) in enumerate(tiles):
        x = 0.05 + (i % 3) * 0.31
        y = 0.895 - (i // 3) * 0.062
        fig.patches.append(plt.Rectangle((x - 0.008, y - 0.022), 0.29, 0.056, transform=fig.transFigure,
                                         facecolor="white", edgecolor=GRID, linewidth=0.8))
        fig.text(x, y + 0.02, label, fontsize=7.5, color=INK2)
        color = INK if delta is None else (GOOD_TEXT if delta >= 0 else BAD_TEXT)
        fig.text(x, y - 0.002, value, fontsize=14, fontweight="bold", color=color)
        fig.text(x, y - 0.016, sub, fontsize=6.5, color=MUTED)

    # equity chart + drawdown panel
    eq = series["equity"]
    ax1 = fig.add_axes([0.08, 0.545, 0.74, 0.225])
    ax2 = fig.add_axes([0.08, 0.465, 0.74, 0.06], sharex=ax1)
    for ax in (ax1, ax2):
        _style_axes(ax)
    fig.text(0.05, 0.79, "Growth since inception (indexed to 100)", fontsize=9, fontweight="bold")
    if len(eq) >= 2:
        idx = pd.to_datetime(list(eq.index))
        lines = {"Core & Shield": eq / eq.iloc[0] * 100}
        for name in ("60/40", "SPY"):
            bser = series["bench"][name].reindex(eq.index).ffill()
            lines[name] = bser / bser.iloc[0] * 100
        for name, s in lines.items():
            ax1.plot(idx, s.values, color=SERIES[name], linewidth=1.6, label=name,
                     zorder=3 if name == "Core & Shield" else 2)
            dd = (s / s.cummax() - 1) * 100
            if name != "SPY":
                ax2.plot(idx, dd.values, color=SERIES[name], linewidth=1.2)
        # direct end labels, nudged apart so they never collide
        ends = sorted(((s.iloc[-1], name) for name, s in lines.items()))
        lo_v = min(float(s.min()) for s in lines.values())
        hi_v = max(float(s.max()) for s in lines.values())
        gap = max(hi_v - lo_v, 0.5) * 0.07
        placed = []
        for v, name in ends:
            y = v if not placed or v - placed[-1] >= gap else placed[-1] + gap
            placed.append(y)
            ax1.annotate(f"{name} {v:.1f}", (idx[-1], y), xytext=(5, 0), textcoords="offset points",
                         fontsize=7, color=INK2, va="center", annotation_clip=False)
        ax1.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, fontsize=7, frameon=False,
                   labelcolor=INK2, handlelength=1.6)
        ax2.set_ylabel("Drawdown %", fontsize=7, color=MUTED)
        ax1.margins(x=0.01)
        import matplotlib.dates as mdates
        loc = mdates.AutoDateLocator(minticks=3, maxticks=7)
        ax2.xaxis.set_major_locator(loc)
        ax2.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc, show_offset=False))
    else:
        ax1.text(0.5, 0.5, "Not enough history yet: the chart starts after the first trading month.",
                 ha="center", va="center", fontsize=8, color=MUTED, transform=ax1.transAxes)
        ax1.set_xticks([]); ax1.set_yticks([]); ax2.set_xticks([]); ax2.set_yticks([])
    plt.setp(ax1.get_xticklabels(), visible=False)

    # holdings + next month
    fig.text(0.05, 0.43, "Held this month", fontsize=9, fontweight="bold")
    hrows = [[r["symbol"], r["sleeve"], f"{r['weight_pct']:.0f}%", fmt_pct(r["return_pct"]),
              fmt_pct(r["contribution_pct"])] for r in metrics["holdings"]]
    _table(fig.add_axes([0.05, 0.255, 0.5, 0.165]),
           ["ETF", "Sleeve", "Weight", "Month return", "Contribution"], hrows,
           [0.14, 0.28, 0.16, 0.22, 0.22], ["left", "left", "right", "right", "right"])
    nm = metrics["next_month"] or "next month"
    fig.text(0.6, 0.43, f"Planned allocation for {nm}", fontsize=9, fontweight="bold")
    nrows = [[r["symbol"], f"{r['core_pct']:.0f}%", f"{r['shield_pct']:.0f}%", f"{r['total_pct']:.0f}%"]
             for r in metrics["next_allocation"]]
    _table(fig.add_axes([0.6, 0.255, 0.35, 0.165]), ["ETF", "Core", "Shield", "Total"], nrows,
           [0.25, 0.25, 0.25, 0.25], ["left", "right", "right", "right"])

    # versus history
    fig.text(0.05, 0.238, "Versus the 2009–2026 backtest", fontsize=9, fontweight="bold")
    for i, c in enumerate(metrics["checks"]):
        y = 0.218 - i * 0.017
        color, word = STATUS[c["status"]]
        fig.text(0.05, y, "●", fontsize=9, color=color, va="center")
        fig.text(0.07, y, f"{c['check']}: {c['value']}", fontsize=7.5, color=INK, va="center")
        fig.text(0.40, y, word, fontsize=7.5, color=INK, fontweight="bold", va="center")
        fig.text(0.58, y, c["reference"], fontsize=7, color=MUTED, va="center")

    # commentary
    fig.text(0.05, 0.135, "Commentary", fontsize=9, fontweight="bold")
    y = 0.117
    for note in (notes or ["No commentary was provided for this month."])[:3]:
        for j, line in enumerate(textwrap.wrap(note, 115)[:3]):
            fig.text(0.05, y, ("•  " if j == 0 else "    ") + line, fontsize=7.5, color=INK, va="top")
            y -= 0.013
        y -= 0.004

    fig.text(0.05, 0.028, "Paper trading, not investment advice. Past and backtested results do not "
             "guarantee future results.", fontsize=6, color=MUTED)
    fig.text(0.05, 0.016, "Backtest reference 2009–2026 (memory/BACKTEST-SUMMARY.md): Core & Shield "
             "7.5%/yr, Sharpe ~1.1, month-end max DD −11% (60/40: 10.2%/yr, Sharpe ~1.1, −19%).",
             fontsize=6, color=MUTED)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format=path.suffix.lstrip(".") or "pdf", facecolor=SURFACE, dpi=110)
    plt.close(fig)


def read_notes(path: str | None) -> list[str]:
    if not path:
        return []
    p = pathlib.Path(path)
    if not p.exists():
        return []
    out = [ln.strip().lstrip("-•* ").strip() for ln in p.read_text(encoding="utf-8").splitlines()]
    return [ln for ln in out if ln][:3]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--month")
    ap.add_argument("--date")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--metrics-only", action="store_true")
    ap.add_argument("--notes-file")
    args = ap.parse_args(argv)
    try:
        cfg = raam.load_config()
        client = raam.Alpaca()
        d = dt.date.fromisoformat(args.date) if args.date else raam.today_et()
        if args.month:
            month = args.month
        else:
            info = raam.calendar_info(client, d)
            if not info["is_last_trading_day"] and not args.force:
                out = {"status": "noop", "reason": f"{d} is not the last trading day of the month "
                                                   f"(that is {info['last_trading_day']})"}
                print(json.dumps(out, indent=2))
                return 0
            month = raam.month_key(d)
        as_of = d if not args.month else month_bounds(month)[1]
        metrics, series = build(client, cfg, month, min(as_of, raam.today_et()))
        if args.metrics_only:
            out = {"status": "ok", "metrics": metrics}
        else:
            path = reports_dir() / f"{month}.pdf"
            render(metrics, series, read_notes(args.notes_file), path)
            out = {"status": "ok", "file": str(path.relative_to(raam.ROOT)), "metrics": metrics}
        code = 0
    except raam.Halt as e:
        out, code = {"status": "halt", "reason": str(e)}, 2
    except Exception as e:  # noqa: BLE001 - report everything as JSON for Claude
        out, code = {"status": "error", "reason": f"{type(e).__name__}: {e}"}, 1
    print(json.dumps(out, indent=2, default=str))
    return code


if __name__ == "__main__":
    sys.exit(main())
