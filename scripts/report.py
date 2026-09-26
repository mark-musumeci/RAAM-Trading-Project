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
ACCOUNT = "#1baf7a"                 # account line/area (reference palette slot 3; labelled directly)
BENCH = "#898781"                   # 60/40 comparison line: neutral, recessive
PILL_BG, CARD_BG = "#f0efec", "#f5f5f2"
UP_ARROW, DOWN_ARROW = "#0ca30c", "#d03b3b"
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
    """Date of the first executed rebalance (when money was first invested); None before that."""
    dates = []
    for p in sorted(raam.SIGNALS_DIR.glob("*.json")):
        ex = json.loads(p.read_text(encoding="utf-8")).get("executed")
        if ex and (ex.get("date") or ex.get("at")):
            dates.append(dt.date.fromisoformat((ex.get("date") or ex["at"])[:10]))
    return min(dates) if dates else None


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

    invested = inc is not None and inc <= end
    b_month = {k: pr(v, start, end) for k, v in bench.items()}
    if invested:
        eq = eq[eq.index >= min(start, inc - dt.timedelta(days=1))]
        month_ret = pr(eq, start, end)
        since = round((eq.iloc[-1] / eq.iloc[0] - 1) * 100, 3) if len(eq) >= 2 else None
        b_since = {k: pr(v, eq.index[0], end) if len(eq) >= 2 else None for k, v in bench.items()}
        max_dd = round(float((eq / eq.cummax() - 1).min() * 100), 3) if len(eq) >= 2 else None
    else:                                    # still all cash: comparisons would be meaningless
        month_ret, since, max_dd = None, None, None
        b_since = {k: None for k in bench}

    def trailing(months: int):
        if not invested or len(eq) < 2:
            return None
        anchor = (pd.Timestamp(end) - pd.DateOffset(months=months)).date()
        if anchor < eq.index[0]:
            return None
        base = eq[eq.index <= anchor].iloc[-1]
        return round(float(eq.iloc[-1] / base - 1) * 100, 3)
    period_returns = {"1 mo": month_ret, "3 mo": trailing(3), "6 mo": trailing(6),
                      "1 yr": trailing(12), "All": since}
    equity_end = round(float(eq.iloc[-1]), 2) if len(eq) else None
    contributions = round(float(eq.iloc[0]), 2) if invested and len(eq) else equity_end
    return_usd = (round(equity_end - contributions, 2)
                  if invested and equity_end is not None and contributions is not None else None)

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
    if not invested:
        checks.append(("Monthly return", "n/a", "na", "not invested yet: first rebalance pending"))
    elif month_ret is None:
        checks.append(("Monthly return", "n/a", "na", "no equity data for the month"))
    else:
        st = "normal" if lo <= month_ret <= hi else ("unusual" if xlo <= month_ret <= xhi else "outside")
        checks.append(("Monthly return", fmt_pct(month_ret), st,
                       f"most backtest months were {lo:+g}% to {hi:+g}%"))
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
        "equity_end": equity_end, "contributions": contributions, "return_usd": return_usd,
        "period_returns": period_returns,
        "month_return_pct": month_ret, "benchmarks_month_pct": b_month,
        "vs_6040_month_pct": None if month_ret is None or b64 is None else round(month_ret - b64, 3),
        "since_inception_pct": since, "benchmarks_since_inception_pct": b_since,
        "max_drawdown_pct": max_dd, "cash_held_pct": cash_pct,
        "holdings": rows, "next_allocation": next_rows,
        "next_month": next_sig["effective_month"] if next_sig else None,
        "checks": [{"check": c[0], "value": c[1], "status": c[2], "reference": c[3]} for c in checks],
    }
    metrics["invested"] = invested
    series = {"equity": eq if invested else eq.iloc[0:0], "bench": bench}
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


def _money(x) -> str:
    if x is None:
        return "n/a"
    return f"−${abs(x):,.2f}" if x < 0 else f"${x:,.2f}"


def _gradient_area(ax, x, y, color, floor):
    """Line with a soft vertical gradient fill down to `floor` (app-style area chart)."""
    import matplotlib.colors as mcolors
    import matplotlib.dates as mdates
    from matplotlib.patches import Polygon
    xn = mdates.date2num(x)
    rgb = mcolors.to_rgb(color)
    grad = np.zeros((120, 1, 4))
    grad[:, :, :3] = rgb
    grad[:, 0, 3] = np.linspace(0.0, 0.22, 120)
    im = ax.imshow(grad, aspect="auto", origin="lower", zorder=1,
                   extent=[xn[0], xn[-1], floor, float(np.max(y))])
    poly = Polygon(np.vstack([[xn[0], floor], np.column_stack([xn, y]), [xn[-1], floor]]),
                   closed=True, facecolor="none", edgecolor="none")
    ax.add_patch(poly)
    im.set_clip_path(poly)
    ax.plot(x, y, color=color, linewidth=1.8, zorder=3, solid_capstyle="round")


def render(metrics: dict, series: dict, notes: list[str], path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=SURFACE)
    renderer = fig.canvas.get_renderer()
    m_label = dt.date.fromisoformat(metrics["month"] + "-01").strftime("%B %Y")
    as_of = dt.date.fromisoformat(metrics["as_of"]).strftime("%d %b %Y")
    invested = metrics["invested"]
    L, R = 0.06, 0.94

    def box(x, y, w, h, color, radius=0.012):
        fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                          transform=fig.transFigure, facecolor=color, edgecolor="none",
                                          zorder=0))

    # ---------- header strip
    fig.text(L, 0.968, f"{metrics['portfolio']} · Monthly report · {m_label}", fontsize=8.5, color=MUTED)
    started = f"started {metrics['inception']}" if metrics["inception"] else "not yet invested"
    fig.text(R, 0.968, f"Alpaca paper account · {started}", fontsize=8.5, color=MUTED, ha="right")

    # ---------- hero: account value, contributions, return
    fig.text(L, 0.932, "Account value", fontsize=10.5, color=INK2)
    fig.text(0.575, 0.932, f"Values on {as_of}", fontsize=10.5, color=INK2, ha="right")
    fig.text(L, 0.878, _money(metrics["equity_end"]), fontsize=30, fontweight="bold", color=INK)
    fig.text(L, 0.845, "Net contributions", fontsize=10, color=INK2)
    fig.text(L, 0.822, _money(metrics["contributions"]), fontsize=13, fontweight="bold", color=INK)
    fig.text(L, 0.792, "Return", fontsize=10, color=INK2)
    if invested and metrics["return_usd"] is not None:
        ret, pct = metrics["return_usd"], metrics["since_inception_pct"] or 0.0
        t = fig.text(L, 0.769, f"{_money(ret)}   {pct:+.2f}%", fontsize=13, fontweight="bold", color=INK)
        bb = t.get_window_extent(renderer).transformed(fig.transFigure.inverted())
        fig.text(bb.x1 + 0.008, 0.771, "▲" if pct >= 0 else "▼", fontsize=11,
                 color=UP_ARROW if pct >= 0 else DOWN_ARROW)
    else:
        fig.text(L, 0.769, "Not invested yet · first rebalance pending", fontsize=12, color=MUTED)

    # ---------- right card: this month vs 60/40
    box(0.60, 0.768, R - 0.60, 0.172, CARD_BG)
    b = metrics["benchmarks_month_pct"]
    diff = metrics["vs_6040_month_pct"]
    fig.text(0.625, 0.915, f"This month · {m_label}", fontsize=9, color=INK2)
    card = [("Core & Shield", fmt_pct(metrics["month_return_pct"]) if invested else "not invested", INK),
            ("60/40 benchmark", fmt_pct(b.get("60/40")), INK),
            ("Difference", "n/a" if diff is None else f"{diff:+.2f} pp",
             INK if diff is None else (GOOD_TEXT if diff >= 0 else BAD_TEXT)),
            ("Cash (BIL) held", "n/a" if metrics["cash_held_pct"] is None
             else f"{metrics['cash_held_pct']:.0f}%", INK),
            ("Max drawdown", fmt_pct(metrics["max_drawdown_pct"], signed=False), INK)]
    for i, (k, v, col) in enumerate(card):
        y = 0.889 - i * 0.025
        fig.text(0.625, y, k, fontsize=9, color=INK2, va="center")
        fig.text(R - 0.022, y, v, fontsize=9.5, fontweight="bold", color=col, va="center", ha="right")

    # ---------- period selector strip (returns per period; "All" shown as the selected pill)
    pr = metrics["period_returns"]
    box(L, 0.702, R - L, 0.046, PILL_BG, radius=0.023)
    keys = ["1 mo", "3 mo", "6 mo", "1 yr", "All"]
    seg = (R - L) / len(keys)
    for i, k in enumerate(keys):
        cx = L + seg * (i + 0.5)
        sel = k == "All"
        if sel:
            box(L + seg * i + 0.006, 0.706, seg - 0.012, 0.038, INK, radius=0.019)
        v = pr.get(k)
        fig.text(cx, 0.731, k, fontsize=9.5, ha="center", va="center",
                 color="white" if sel else INK, fontweight="bold" if sel else "normal")
        fig.text(cx, 0.715, "n/a" if v is None else f"{v:+.2f}%", fontsize=8, ha="center", va="center",
                 color="white" if sel else (MUTED if v is None else INK2))

    # ---------- area chart: account value (with 60/40 on the same starting value)
    ax = fig.add_axes([L, 0.43, 0.80, 0.25])
    ax.set_facecolor(SURFACE)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(length=0, colors=MUTED, labelsize=8)
    eq = series["equity"]
    if invested and len(eq) >= 2:
        idx = pd.to_datetime(list(eq.index))
        acct = eq.values.astype(float)
        bser = series["bench"]["60/40"].reindex(eq.index).ffill().bfill()
        bench = (bser / bser.iloc[0] * acct[0]).values
        lo = float(min(acct.min(), bench.min()))
        hi = float(max(acct.max(), bench.max()))
        pad = max(hi - lo, hi * 0.01) * 0.08
        floor, top = lo - pad, hi + pad
        ax.set_ylim(floor, top)
        ax.set_xlim(idx[0], idx[-1])
        ax.plot(idx, bench, color=BENCH, linewidth=1.1, zorder=2, label="60/40 (same starting value)")
        _gradient_area(ax, idx, acct, ACCOUNT, floor)
        ax.plot([], [], color=ACCOUNT, linewidth=1.8, label="Core & Shield account")
        ticks = [floor + (top - floor) * f for f in (0.08, 0.5, 0.92)]
        ax.set_yticks(ticks)
        ax.yaxis.tick_right()
        ax.set_yticklabels([f"${v:,.2f}" for v in ticks], fontsize=8, color=MUTED)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        n = 4 if len(idx) > 4 else len(idx)
        xt = [idx[int(round(j))] for j in np.linspace(0, len(idx) - 1, n)]
        ax.set_xticks(xt)
        ax.set_xticklabels([d.strftime("%d/%m/%Y") for d in xt], fontsize=8, color=MUTED)
        ax.legend(loc="upper left", fontsize=7.5, frameon=False, labelcolor=INK2, handlelength=1.6)
    else:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axhline(0.5, color=GRID, linewidth=0.8)
        ax.text(0.5, 0.62, "The account chart starts after the first rebalance.",
                ha="center", va="center", fontsize=9, color=MUTED, transform=ax.transAxes)

    # ---------- held / planned
    fig.text(L, 0.385, f"Held in {m_label}", fontsize=10, fontweight="bold")
    hrows = [[r["symbol"], r["sleeve"], f"{r['weight_pct']:.0f}%", fmt_pct(r["return_pct"]),
              fmt_pct(r["contribution_pct"])] for r in metrics["holdings"]]
    _table(fig.add_axes([L, 0.215, 0.46, 0.16]),
           ["ETF", "Sleeve", "Weight", "Return", "Contrib."], hrows,
           [0.14, 0.30, 0.16, 0.2, 0.2], ["left", "left", "right", "right", "right"])
    nm = metrics["next_month"]
    nm_label = dt.date.fromisoformat(nm + "-01").strftime("%B %Y") if nm else "next month"
    fig.text(0.58, 0.385, f"Planned for {nm_label}", fontsize=10, fontweight="bold")
    nrows = [[r["symbol"], f"{r['core_pct']:.0f}%", f"{r['shield_pct']:.0f}%", f"{r['total_pct']:.0f}%"]
             for r in metrics["next_allocation"]]
    _table(fig.add_axes([0.58, 0.215, R - 0.58, 0.16]), ["ETF", "Core", "Shield", "Total"], nrows,
           [0.25, 0.25, 0.25, 0.25], ["left", "right", "right", "right"])

    # ---------- versus backtest (2 x 2 grid)
    fig.text(L, 0.195, "Versus the backtest", fontsize=10, fontweight="bold")
    for i, c in enumerate(metrics["checks"][:4]):
        x = L if i % 2 == 0 else 0.52
        y = 0.176 - (i // 2) * 0.031
        color, word = STATUS[c["status"]]
        fig.text(x, y, "●", fontsize=9, color=color, va="center")
        label = f"{c['check']}: {c['value']}" + ("" if c["status"] == "na" else f" · {word}")
        fig.text(x + 0.02, y, label, fontsize=8, color=INK, va="center")
        fig.text(x + 0.02, y - 0.012, c["reference"], fontsize=6.8, color=MUTED, va="center")

    # ---------- commentary
    fig.text(L, 0.106, "Commentary", fontsize=10, fontweight="bold")
    y = 0.091
    for note in (notes or ["No commentary was provided for this month."])[:3]:
        for j, line in enumerate(textwrap.wrap(note, 118)[:2]):
            fig.text(L, y, ("•  " if j == 0 else "    ") + line, fontsize=7.8, color=INK, va="top")
            y -= 0.0125
        y -= 0.004

    fig.text(L, 0.026, "Paper trading, not investment advice. Past and backtested results do not "
             "guarantee future results.", fontsize=6.3, color=MUTED)
    fig.text(L, 0.014, "Backtest 2015–2026: Core & Shield + IBIT 9.3%/yr, Sharpe ~1.2, max DD −14.1% · "
             "60/40 9.2%/yr, Sharpe ~0.9, max DD −19%.",
             fontsize=6.3, color=MUTED)
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
