#!/usr/bin/env python3
"""Build the README images (docs/images/*.png) from the repo's own results files.

Sources: backtest/results/monthly_live.csv, summary.json, stress.json, robustness.json.
Palette: the validated reference categorical slots 1-3 (blue, orange, aqua), all-pairs safe;
aqua sits below 3:1 on the light surface, so every series is also direct-labelled.
Type is sized for GitHub's ~900-1000 px README column (images are downscaled about 2x).

Usage: python docs/build_readme_assets.py
"""
from __future__ import annotations

import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "backtest" / "results"
OUT = ROOT / "docs" / "images"

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"          # validated slots 1-3
CS, B6040, SPY = AQUA, BLUE, ORANGE                            # colour follows the entity
TINT = {"blue": ("#e9f1fb", BLUE, BLUE), "aqua": ("#e4f5ee", AQUA, "#0f7a55"),
        "orange": ("#fdeee7", ORANGE, "#c2410c"), "sand": ("#fbf3e3", "#c98500", "#8a5a00"),
        "grey": ("#f2f1ee", "#a8a69f", INK)}
plt.rcParams.update({"font.family": "DejaVu Sans", "text.hinting": "none"})
TICK, LABEL = 13, 13.5


def pct(v, nd=1, signed=False):
    s = f"{abs(v):.{nd}f}%"
    return ("−" if v < 0 else ("+" if signed and v > 0 else "")) + s


def style(ax, grid="y"):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(BASELINE)
        ax.spines[s].set_linewidth(0.9)
    ax.tick_params(colors=MUTED, labelsize=TICK, length=0)
    if grid:
        ax.grid(axis=grid, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def title(fig, text, sub=None):
    fig.text(0.04, 0.955, text, fontsize=21, fontweight="bold", color=INK, va="top")
    if sub:
        fig.text(0.04, 0.885, sub, fontsize=14, color=INK2, va="top")


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=150, facecolor=SURFACE)
    plt.close(fig)
    print("wrote", OUT / name)


# ============================================================================ hero diagram
def panel(ax, x, y, w, h, tint, label):
    fill, edge, ink = TINT[tint]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4",
                                facecolor=fill, edgecolor=edge, linewidth=1.8, zorder=1))
    ax.text(x + 1.6, y + h - 3.2, label, fontsize=19, fontweight="bold", color=ink, va="center", zorder=5)


def card(ax, x, y, w, h, head, body, tint, hs=15.5, bs=13.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.9",
                                facecolor="white", edgecolor=TINT[tint][1], linewidth=1.4, zorder=3))
    ax.text(x + 1.3, y + h - 2.1, head, fontsize=hs, fontweight="bold", color=INK, va="top", zorder=4)
    ax.text(x + 1.3, y + h - 6.0, body, fontsize=bs, color=INK2, va="top", zorder=4, linespacing=1.35)


def arrow(ax, p0, p1, color, lw=2.2):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=20, color=color, linewidth=lw,
                                 zorder=6, shrinkA=0, shrinkB=0))


def hero():
    fig = plt.figure(figsize=(16, 9.6))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 96)
    ax.axis("off")
    ax.text(3, 91.5, "How Core & Shield runs each month", fontsize=27, fontweight="bold", color=INK, va="center")
    ax.text(3, 86.3, "A deterministic engine decides  ·  Claude operates it  ·  every step logged to Git",
            fontsize=16, color=INK2, va="center")

    top, bottom = 80.5, 25
    # 1 Inputs
    panel(ax, 2, bottom, 30, top - bottom, "sand", "1  Inputs")
    card(ax, 3.6, 57.5, 26.8, 14.5, "Market data", "Alpaca daily prices\n14 ETFs, 800 days", "sand")
    card(ax, 3.6, 41.5, 26.8, 14.5, "Research gate", "fund closures, halts\ncan only stop a signal", "sand")
    card(ax, 3.6, 26.5, 26.8, 13.5, "Fixed rules", "config/raam.json\nowner-only changes", "sand")
    # 2 Signal engine
    panel(ax, 35, bottom, 41, top - bottom, "aqua", "2  Signal engine")
    for i, (h, b) in enumerate((("Momentum", "84-day\nreturn"), ("Volatility", "EWMA\nλ 0.94"),
                                ("Correlation", "vs the\nother 11"))):
        card(ax, 36.6 + i * 12.9, 57.5, 12.3, 14.5, h, b, "aqua", hs=12, bs=13)
    card(ax, 36.6, 40.5, 38.0, 13.5, "Rank 12, keep the best 5", "11 diversified ETFs + spot Bitcoin\n"
         "score = average of the three ranks", "aqua")
    card(ax, 36.6, 26.5, 38.0, 11.5, "Cash test", "a pick must beat T-bill momentum,\nor its slot goes to cash",
         "aqua")
    for x in (42.6, 55.6, 68.6):
        arrow(ax, (x, 57.5), (x, 54.2), AQUA)
    arrow(ax, (55.6, 40.5), (55.6, 38.2), AQUA)
    # 3 Portfolio
    panel(ax, 79, bottom, 37, top - bottom, "blue", "3  Portfolio")
    card(ax, 80.6, 57.5, 33.8, 14.5, "Core · 50% · growth", "QQQM (Nasdaq-100) if above its\n10-month average, else T-bills", "blue")
    card(ax, 80.6, 41.5, 33.8, 14.5, "Shield · 50% · rotating", "5 picks × 10% each\ndefends when trends break",
         "blue")
    card(ax, 80.6, 26.5, 33.8, 13.5, "Caps", "Bitcoin ≤ 5% of portfolio\nno order > 55% of equity", "blue")
    # 4 Risk + execution
    panel(ax, 119, 47, 39, top - 47, "orange", "4  Risk guardrails")
    ax.text(120.8, 71.5, "•  weights must sum to 100%\n•  universe tickers only\n•  market open, paper account\n"
                         "•  stale or blank prices → halt\n•  breaker: −20% from peak or\n    −5% in a day → all cash",
            fontsize=13.5, color=INK2, va="top", linespacing=1.5, zorder=5)
    ax.add_patch(FancyBboxPatch((119, bottom), 39, 18, boxstyle="round,pad=0,rounding_size=1.6",
                                facecolor=BLUE, edgecolor=BLUE, zorder=3))
    ax.text(138.5, 37.8, "Execution", fontsize=24, fontweight="bold", color="white", ha="center", va="center",
            zorder=5)
    ax.text(138.5, 30.6, "Alpaca paper · 1st trading day\nsells, then buys · slippage logged", fontsize=13,
            color="white", ha="center", va="center", zorder=5, linespacing=1.35)
    # flow arrows between panels
    arrow(ax, (32, 64.7), (35, 64.7), TINT["sand"][1])
    arrow(ax, (32, 48.7), (35, 48.7), TINT["sand"][1])
    arrow(ax, (76, 33), (79, 48.7), INK2)
    arrow(ax, (116, 52), (119, 60), INK2)
    arrow(ax, (138.5, 47), (138.5, 43.2), ORANGE)
    # Operations band
    ax.add_patch(FancyBboxPatch((2, 2), 156, 19, boxstyle="round,pad=0,rounding_size=1.4", facecolor=TINT["grey"][0],
                                edgecolor=TINT["grey"][1], linewidth=1.4, linestyle=(0, (5, 4)), zorder=1))
    ax.text(3.6, 18.2, "Operations  ·  Claude Code cloud routines  ·  operator, not strategist", fontsize=16,
            fontweight="bold", color=INK, va="center")
    for i, (h, b) in enumerate((("Morning", "10:45 ET · rebalance"), ("Close", "17:30 ET · health, signal"),
                                ("Report", "19:00 ET · monthly PDF"), ("Memory", "GitHub repo"),
                                ("Alerts", "Discord · ⚠ on any halt"))):
        card(ax, 3.6 + i * 30.8, 3.6, 29.2, 10.6, h, b, "grey", hs=14.5, bs=13)
    save(fig, "architecture.png")


# ============================================================================ charts
def load_monthly():
    return pd.read_csv(RES / "monthly_live.csv", parse_dates=["entry", "exit"])


def spread_labels(values: list[float], min_gap: float) -> list[float]:
    """Nudge label positions (in plot units) apart so they never overlap, keeping order."""
    order = np.argsort(values)
    pos = np.array(values, dtype=float)
    for a, b in zip(order[:-1], order[1:]):
        if pos[b] - pos[a] < min_gap:
            pos[b] = pos[a] + min_gap
    return list(pos)


def growth(p):
    fig = plt.figure(figsize=(13, 8))
    fig.patch.set_facecolor(SURFACE)
    title(fig, "Growth of $100,000, Feb 2015 – Sep 2026",
          "Backtest of the live rules · next-open fills · 5 bps per trade · Bitcoin before 2024 simulated")
    ax = fig.add_axes([0.08, 0.38, 0.76, 0.45])
    ax2 = fig.add_axes([0.08, 0.07, 0.76, 0.21], sharex=ax)
    style(ax)
    style(ax2)
    x = pd.concat([pd.Series([p["entry"].iloc[0]]), p["exit"]], ignore_index=True)
    series = [("SPY", "spy", SPY, 1.8), ("60/40", "b6040", B6040, 2.1), ("Core & Shield", "ret", CS, 2.8)]
    ends = {}
    for name, col, c, lw in series:
        eq = pd.Series(np.r_[1.0, (1 + p[col]).cumprod().values] * 100_000)
        ax.plot(x, eq, color=c, linewidth=lw, solid_capstyle="round")
        ends[name] = eq.iloc[-1]
        if col != "spy":
            dd = (eq / eq.cummax() - 1) * 100
            ax2.plot(x, dd, color=c, linewidth=lw * 0.75)
            ax2.fill_between(x, dd, 0, color=c, alpha=0.14 if col == "ret" else 0.07, linewidth=0)
            ends[name + "_dd"] = dd.min()
    ax.set_yscale("log")
    logs = spread_labels([np.log10(ends[n]) for n, *_ in series], 0.05)
    for (name, *_), ly in zip(series, logs):
        ax.text(x.iloc[-1] + pd.Timedelta(days=45), 10 ** ly, f"{name}  ${ends[name] / 1000:,.0f}k",
                fontsize=LABEL, color=INK, va="center", fontweight="bold" if name == "Core & Shield" else "normal")
    ax.set_yticks([100_000, 150_000, 200_000, 300_000, 400_000])
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v / 1000:,.0f}k"))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.tick_params(labelbottom=False)
    handles = [plt.Line2D([], [], color=c, linewidth=3) for _, _, c, _ in series]
    ax.legend(handles, [s[0] for s in series], frameon=False, fontsize=LABEL, loc="upper left", labelcolor=INK2)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: pct(v, 0)))
    ax2.set_yticks([0, -10, -20])
    ax2.text(0.0, 1.06, "Drawdown from peak (month-end)", transform=ax2.transAxes, fontsize=LABEL, color=INK2)
    ax2.text(x.iloc[-1] + pd.Timedelta(days=45), -9.5,
             f"worst\nC&S  {pct(ends['Core & Shield_dd'])}\n60/40  {pct(ends['60/40_dd'])}",
             fontsize=LABEL, color=INK, va="center", linespacing=1.35)
    save(fig, "growth.png")


def years(p):
    cy = p.assign(year=p["entry"].dt.year).groupby("year").agg(
        cs=("ret", lambda r: ((1 + r).prod() - 1) * 100), b=("b6040", lambda r: ((1 + r).prod() - 1) * 100))
    fig = plt.figure(figsize=(13, 6))
    fig.patch.set_facecolor(SURFACE)
    title(fig, "Calendar-year returns vs 60/40", "Ahead when markets fall, behind in strong equity years · 2026 to September")
    ax = fig.add_axes([0.07, 0.1, 0.91, 0.66])
    style(ax)
    xs = np.arange(len(cy))
    w = 0.38
    ax.bar(xs - w / 2 - 0.015, cy["cs"], w, color=CS, label="Core & Shield")
    ax.bar(xs + w / 2 + 0.015, cy["b"], w, color=B6040, label="60/40")
    ax.axhline(0, color=BASELINE, linewidth=1)
    for i, (a, b) in enumerate(zip(cy["cs"], cy["b"])):
        ax.text(i - w / 2, a + (0.8 if a >= 0 else -0.8), f"{a:.0f}".replace("-", "−") if abs(a) >= 0.5 else "0",
                ha="center",
                va="bottom" if a >= 0 else "top", fontsize=12, color=INK2)
    ax.set_xticks(xs, [str(y) for y in cy.index])
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: pct(v, 0)))
    ax.legend(frameon=False, fontsize=LABEL, loc="upper right", labelcolor=INK2)
    save(fig, "calendar_years.png")


def random_picks():
    r = json.load(open(RES / "robustness.json", encoding="utf-8"))
    fig = plt.figure(figsize=(13, 6.2))
    fig.patch.set_facecolor(SURFACE)
    title(fig, "Skill or luck? The live ranking vs 1,000 random-pick portfolios",
          "Identical rules, dates and costs; only the Shield's 5 picks are random each month")
    for k, (win, label) in enumerate((("A", "2015–2026, with Bitcoin"), ("B", "2008–2026, without Bitcoin"))):
        x = r[win]["port"]
        ax = fig.add_axes([0.05 + k * 0.49, 0.13, 0.43, 0.56])
        style(ax, grid=None)
        sh = np.array(x["random_sharpe"])
        ax.hist(sh, bins=32, color=B6040, alpha=0.5, edgecolor=SURFACE, linewidth=0.8)
        real = x["real"]["Sharpe"]
        ax.axvline(real, color=CS, linewidth=3.2)
        ymax = ax.get_ylim()[1]
        ax.set_ylim(0, ymax * 1.25)
        ax.text(real, ymax * 1.2, f"Live ranking: Sharpe {real:.2f}\nbeats {x['beats_random_pct']['Sharpe']:.0f}% "
                                  "of random", fontsize=LABEL, color=INK, va="top", ha="right", fontweight="bold")
        ax.text(sh.min(), ymax * 0.55, f"random\nmedian\n{np.median(sh):.2f}", fontsize=12, color=INK2, va="center")
        ax.text(0, 1.04, label, transform=ax.transAxes, fontsize=15, color=INK, fontweight="bold")
        ax.set_xlabel("Sharpe ratio, whole portfolio (rf = 0)", fontsize=12.5, color=MUTED)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
    save(fig, "random_picks.png")


def stress():
    t = json.load(open(RES / "stress.json", encoding="utf-8"))
    s = json.load(open(RES / "summary.json", encoding="utf-8"))
    p = load_monthly()
    y22 = p[p["entry"].dt.year == 2022]
    rows = [("2022 (real)", ((1 + y22["ret"]).prod() - 1) * 100, ((1 + y22["b6040"]).prod() - 1) * 100),
            ("Jun 2008–Jun 2009 (real, no BTC)", s["crisis_2008"]["Core & Shield (no Bitcoin)"]["Total %"],
             s["crisis_2008"]["60/40"]["Total %"])]
    names = {"Crash day": "−20% crash day*", "Stocks and bonds": "Stocks & bonds fall*", "Stagflation": "Stagflation*"}
    for key, ev in t["shocks"].items():
        for k, lab in names.items():
            if key.startswith(k):
                rows.append((lab, float(np.mean([e["loss %"] for e in ev])),
                             float(np.mean([e["60/40 loss %"] for e in ev]))))
    fig = plt.figure(figsize=(13, 6.2))
    fig.patch.set_facecolor(SURFACE)
    title(fig, "Losses in real and simulated crises",
          "* simulated: shock injected into real prices at 6 dates, full model re-run, average shown")
    ax = fig.add_axes([0.25, 0.08, 0.72, 0.7])
    style(ax, grid="x")
    ys = np.arange(len(rows))[::-1]
    h = 0.36
    ax.barh(ys + h / 2 + 0.015, [r[1] for r in rows], h, color=CS, label="Core & Shield")
    ax.barh(ys - h / 2 - 0.015, [r[2] for r in rows], h, color=B6040, label="60/40")
    for y, (_, a, b) in zip(ys, rows):
        ax.text(a - 0.4, y + h / 2, pct(a), va="center", ha="right", fontsize=12, color=INK2)
        ax.text(b - 0.4, y - h / 2, pct(b), va="center", ha="right", fontsize=12, color=INK2)
    ax.set_yticks(ys, [r[0] for r in rows])
    ax.tick_params(axis="y", labelsize=LABEL, colors=INK)
    ax.set_xlim(min(r[2] for r in rows) * 1.2, 0)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: pct(v, 0)))
    ax.legend(frameon=False, fontsize=LABEL, loc="lower left", labelcolor=INK2)
    save(fig, "stress.png")


# ============================================================================ stage cards (a real month)
GOOD, BAD = "#006300", "#c2410c"


def stage(name, tint, role, goal, draw_output, out_title, when, where):
    """'Goal' card on the left, a real example of the stage's output on the right."""
    fill, edge, ink = TINT[tint]
    fig = plt.figure(figsize=(13, 4.3))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 130)
    ax.set_ylim(0, 43)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((1.5, 2), 40, 39, boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor=fill, edgecolor=edge, linewidth=1.6))
    ax.add_patch(FancyBboxPatch((3.5, 30.5), 9, 8.5, boxstyle="round,pad=0,rounding_size=1",
                                facecolor=edge, edgecolor=edge))
    ax.text(8, 34.75, role[0], fontsize=22, fontweight="bold", color="white", ha="center", va="center")
    ax.text(14.5, 36.6, role, fontsize=17, fontweight="bold", color=ink, va="center")
    ax.text(14.5, 32.4, "Goal", fontsize=12.5, color=MUTED, va="center")
    ax.text(3.6, 26.5, goal, fontsize=13.5, color=INK, va="top", linespacing=1.45)
    for i, (k, v) in enumerate((("When", when), ("Code", where))):
        y = 9.6 - i * 4.6
        ax.text(3.6, y, k, fontsize=11.5, color=MUTED, va="baseline")
        ax.text(10.5, y, v, fontsize=11.5, color=INK2, va="baseline",
                family="DejaVu Sans Mono" if k == "Code" else "DejaVu Sans")
    ax.add_patch(FancyArrowPatch((42.5, 21.5), (46.5, 21.5), arrowstyle="-|>", mutation_scale=20, color=edge,
                                 linewidth=2.2))
    ax.add_patch(FancyBboxPatch((47.5, 2), 81, 39, boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor="white", edgecolor=edge, linewidth=1.6))
    ax.text(50, 37.4, out_title, fontsize=15, fontweight="bold", color=INK, va="center")
    draw_output(ax)
    save(fig, name)


def stages():
    sig = json.load(open(ROOT / "memory" / "signals" / "2026-09.json", encoding="utf-8"))
    hurdle = sig["momentum_hurdle"]["value_pct"]
    rows = [r for r in sig["table"] if r["selected"]]

    def research(ax):
        lines = [("Flags", "none: no closure, merger, ticker change or halt"),
                 ("Scanned", "iShares, Vanguard, State Street, Invesco funds\n+ Bitcoin ETF custody & regulation checks"),
                 ("Context", "September: yields up sharply; REITs and\nmaterials about −7%; Bitcoin held up"),
                 ("Logged", "memory/RESEARCH-LOG.md, with sources")]
        for i, (k, v) in enumerate(lines):
            y = (30, 24.4, 15.5, 6.6)[i]
            ax.text(50, y, k, fontsize=13, fontweight="bold", color=INK, va="baseline")
            ax.text(62, y, v.split("\n")[0], fontsize=13, color=INK2 if k != "Flags" else GOOD, va="baseline")
            if "\n" in v:
                ax.text(62, y - 3.3, v.split("\n")[1], fontsize=13, color=INK2, va="baseline")

    def engine(ax):
        cols = [(50, "ETF"), (60, "Momentum"), (75, "Rank M·V·C"), (93, "Score"), (104, f"Beats cash ({hurdle:+.2f}%)?")]
        for x, h in cols:
            ax.text(x, 32.3, h, fontsize=12, color=MUTED, va="center")
        ax.plot([50, 126], [30.4, 30.4], color=GRID, linewidth=1)
        for i, r in enumerate(sorted(rows, key=lambda r: r["score"])):
            y = 27.4 - i * 4.9
            ok = r["momentum_pct"] > hurdle
            ax.text(50, y, r["symbol"], fontsize=13.5, fontweight="bold", color=INK, va="center")
            ax.text(60, y, pct(r["momentum_pct"], 1, signed=True), fontsize=13, color=INK2, va="center")
            ax.text(75, y, f"{r['rank_M']:.0f} · {r['rank_V']:.0f} · {r['rank_C']:.0f}", fontsize=13, color=INK2,
                    va="center")
            ax.text(93, y, f"{r['score']:.2f}", fontsize=13, color=INK2, va="center")
            ax.text(104, y, "✓  holds its slot" if ok else "✗  slot → T-bills", fontsize=13,
                    color=GOOD if ok else BAD, va="center", fontweight="bold")

    def portfolio(ax):
        t = sig["targets"]
        parts = [("SPY", t["SPY"], BLUE, "Core"), ("AGG", t["AGG"], "#7fb0ea", "Core"),
                 ("DBC", t["DBC"], AQUA, "Shield"), ("IBIT", t["IBIT"], "#7fd3b4", "Shield"),
                 ("BIL", t["BIL"], "#b9b7af", "Shield + cap")]
        x0, W = 50, 76
        cx = x0
        for sym, w, c, _ in parts:
            ax.add_patch(FancyBboxPatch((cx, 19.5), W * w - 0.4, 9.5, boxstyle="round,pad=0,rounding_size=0.5",
                                        facecolor=c, edgecolor="none"))
            if w >= 0.08:
                ax.text(cx + W * w / 2, 24.25, f"{sym}\n{w * 100:.0f}%", fontsize=13,
                        color="white" if sym != "BIL" else INK, ha="center", va="center", fontweight="bold",
                        linespacing=1.2)
            else:
                ax.text(cx + W * w / 2, 30.6, f"{sym} {w * 100:.0f}%", fontsize=12, color=INK, ha="center",
                        va="bottom", fontweight="bold")
            cx += W * w
        ax.text(50, 32.2, "Core 50%  ·  Shield 50%", fontsize=12.5, color=MUTED, va="center")
        ax.text(50, 15, "•  3 of 5 Shield picks failed the cash test → 30% to T-bills (BIL)", fontsize=13,
                color=INK2, va="center")
        ax.text(50, 10, f"•  IBIT capped: {sig['caps_applied']['IBIT']['uncapped'] * 100:.0f}% → "
                         f"{sig['caps_applied']['IBIT']['cap'] * 100:.0f}%, excess to BIL", fontsize=13, color=INK2,
                va="center")
        ax.text(50, 5, "•  a defensive month: 35% cash while stocks and bonds fell", fontsize=13, color=INK2,
                va="center")

    def execution(ax):
        fills = sig["executed"]["fills"]
        cols = [(50, "Order"), (66, "Fill price"), (84, "Slippage"), (100, "Status")]
        for x, h in cols:
            ax.text(x, 32.3, h, fontsize=12, color=MUTED, va="center")
        ax.plot([50, 126], [30.4, 30.4], color=GRID, linewidth=1)
        for i, f in enumerate(sorted(fills, key=lambda f: -float(f["filled_qty"]) * float(f["filled_avg_price"]))):
            y = 27.4 - i * 4.9
            ax.text(50, y, f"BUY {f['symbol']}", fontsize=13.5, fontweight="bold", color=INK, va="center")
            ax.text(66, y, f"${float(f['filled_avg_price']):,.2f}", fontsize=13, color=INK2, va="center")
            bps = f["slippage_bps"]
            ax.text(84, y, f"{bps:+.1f} bps".replace("-", "−"), fontsize=13, color=INK2, va="center")
            ax.text(100, y, "✓  filled", fontsize=13, color=GOOD, va="center", fontweight="bold")
        ax.text(126, 4, "positive = cost, negative = better than the planned price", fontsize=10.5, color=MUTED,
                ha="right")

    def oversight(ax):
        lines = [("O1", "signal saved on the last trading day, research first"),
                 ("O2", "5 of 5 orders filled on 1 Oct"),
                 ("O6", "slippage ≈ 1.7 bps average (limit 10), worst 10.5"),
                 ("O7", "every holding within 0.3 pp of target"),
                 ("O8", "IBIT ≤ 5% at the rebalance")]
        for i, (k, v) in enumerate(lines):
            y = 31.6 - i * 5.6
            ax.text(50, y, "✓ PASS", fontsize=12.5, color=GOOD, fontweight="bold", va="center")
            ax.text(62, y, k, fontsize=13, fontweight="bold", color=INK, va="center")
            ax.text(68, y, v, fontsize=13, color=INK2, va="center")
        ax.text(50, 4, "Discord:  RAAM rebalanced: BUY SPY, AGG, BIL, DBC, IBIT | all filled",
                fontsize=11, color=MUTED, va="center", family="DejaVu Sans Mono")

    stage("stage_research.png", "sand", "Research gate",
          "Before any signal, check every fund\nfor structural problems. It can stop\nthe signal, never "
          "change a pick.", research, "Output · 30 Sep 2026",
          "last trading day, before the signal", ".claude/commands/research.md")
    stage("stage_engine.png", "aqua", "Signal engine",
          "Rank 12 candidates on momentum,\nvolatility and correlation; keep the\nbest 5 that beat cash.", engine,
          "Output · the 5 selected, 30 Sep 2026", "last trading day, after the close",
          "scripts/raam.py signal")
    stage("stage_portfolio.png", "blue", "Portfolio",
          "Combine the fixed Core with the\nShield picks, then apply the caps.", portfolio,
          "Output · October 2026 allocation (previous 60/40 Core)", "same run as the signal",
          "config/raam.json → portfolio")
    stage("stage_execution.png", "orange", "Execution",
          "After the risk checks, trade at\n~10:45 ET on the first trading day;\nrecord every fill and its cost.",
          execution, "Output · 1 Oct 2026 fills", "first trading day, ~10:45 ET",
          "scripts/raam.py rebalance")
    stage("stage_oversight.png", "grey", "Oversight",
          "Score every month against the\npre-registered evaluation plan;\nreport to Discord.", oversight,
          "Output · first month's operations scorecard", "daily health + monthly review",
          "memory/EVALUATION-PLAN.md")


def main():
    hero()
    stages()
    p = load_monthly()
    growth(p)
    years(p)
    random_picks()
    stress()


if __name__ == "__main__":
    main()
