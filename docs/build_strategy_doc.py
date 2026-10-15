#!/usr/bin/env python3
"""Build the Core & Shield strategy handbook (multi-page PDF) for the owner's reference.

Charts come from backtest/results/monthly_live.csv; the text reflects memory/TRADING-STRATEGY.md,
memory/BACKTEST-SUMMARY.md, memory/EVALUATION-PLAN.md and backtest/results/STRESS.md as of the
version date below. Re-run after any owner-approved rule change and bump VERSION.

Usage: python docs/build_strategy_doc.py [--out docs/Core-and-Shield-Strategy.pdf]
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.hinting"] = "none"          # PNG previews match the PDF spacing
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402
from matplotlib.textpath import TextToPath  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION, VERSION_DATE = "1.2", "14 October 2026"
TITLE = "Core & Shield · Strategy Handbook"

# Same palette as the monthly report (scripts/report.py)
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE, PILL_BG, CARD_BG = "#e1e0d9", "#c3c2b7", "#f0efec", "#f5f5f2"
GREEN, GREY, BLUE, BLUE_L = "#1baf7a", "#898781", "#2a78d6", "#8db8ec"
GOOD, BAD, AMBER = "#006300", "#d03b3b", "#fab219"
FONT = "DejaVu Sans"

W, H = 8.27, 11.69                    # A4, inches
ML, MR, TOP, BOTTOM = 0.8, 0.8, 0.85, 0.85
CW = W - ML - MR                      # content width

_T2P = TextToPath()
_WCACHE: dict = {}


def tw(s: str, size: float, bold: bool) -> float:
    """Rendered width of s in inches."""
    key = (s, size, bold)
    if key not in _WCACHE:
        fp = FontProperties(family=FONT, weight="bold" if bold else "normal", size=size)
        _WCACHE[key] = _T2P.get_text_width_height_descent(s, fp, ismath=False)[0] / 72.0
    return _WCACHE[key]


def space_w(size: float) -> float:
    return tw("a a", size, False) - tw("aa", size, False)


def parse(s: str) -> list[list[tuple[str, bool]]]:
    """'plain **bold**, plain' -> words; each word is a list of (text, bold) pieces that touch."""
    words: list[list[tuple[str, bool]]] = []
    glue = False                       # the next piece continues the previous word (no space between)
    for i, part in enumerate(s.split("**")):
        bold = i % 2 == 1
        for m in re.finditer(r"(\s*)(\S+)", part):
            if glue and not m.group(1) and words:
                words[-1].append((m.group(2), bold))
            else:
                words.append([(m.group(2), bold)])
            glue = True
        glue = (not part[-1].isspace()) if part else glue
    return words


def word_w(word, size: float) -> float:
    return sum(tw(t, size, b) for t, b in word)


def line_w(line, size: float) -> float:
    return sum(word_w(w, size) for w in line) + space_w(size) * max(0, len(line) - 1)


def layout(s: str, size: float, width: float):
    lines, cur, cur_w, sp = [], [], 0.0, space_w(size)
    for w in parse(s):
        ww = word_w(w, size)
        if cur and cur_w + sp + ww > width:
            lines.append(cur)
            cur, cur_w = [], 0.0
        cur_w += (sp if cur else 0.0) + ww
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines or [[]]


def draw_line(fig, line, x: float, y: float, size: float, color: str, bold_color: str | None = None):
    """Draw one laid-out line at (x, y) inches, word by word."""
    sp = space_w(size)
    for w in line:
        for t, b in w:
            fig.text(x / W, y / H, t, fontsize=size, family=FONT, va="baseline",
                     fontweight="bold" if b else "normal", color=(bold_color or color) if b else color)
            x += tw(t, size, b)
        x += sp


class Doc:
    def __init__(self, pdf: PdfPages, png_dir: pathlib.Path | None = None):
        self.pdf, self.fig, self.page, self.png_dir = pdf, None, 0, png_dir
        self.y = H - TOP

    # ---------------------------------------------------------------- pages
    def new_page(self, cover: bool = False):
        self.finish()
        self.page += 1
        self.fig = plt.figure(figsize=(W, H))
        self.fig.patch.set_facecolor(SURFACE)
        self.y = H - TOP
        self.cover = cover

    def finish(self):
        if self.fig is None:
            return
        if not self.cover:
            self.fig.text(ML / W, 0.45 / H, TITLE, fontsize=7.5, color=MUTED, family=FONT)
            self.fig.text((W - MR) / W, 0.45 / H, f"v{VERSION} · {VERSION_DATE} · page {self.page}",
                          fontsize=7.5, color=MUTED, ha="right", family=FONT)
            self.fig.add_artist(Line2D([ML / W, (W - MR) / W], [0.62 / H] * 2, color=GRID, lw=0.6))
        self.pdf.savefig(self.fig, facecolor=SURFACE)
        if self.png_dir:
            self.fig.savefig(self.png_dir / f"page{self.page:02d}.png", dpi=80, facecolor=SURFACE)
        plt.close(self.fig)
        self.fig = None

    def need(self, h: float):
        if self.y - h < BOTTOM:
            self.new_page()

    def gap(self, h: float):
        self.y -= h

    # ---------------------------------------------------------------- text
    def _draw_lines(self, lines, x, size, color, lh):
        for line in lines:
            self.y -= lh
            draw_line(self.fig, line, x, self.y, size, color)

    def text(self, s: str, size: float = 9.2, color: str = INK, indent: float = 0.0,
             width: float | None = None, after: float = 0.08, lh_mult: float = 1.4):
        width = (width or CW) - indent
        lines = layout(s, size, width)
        lh = size * lh_mult / 72
        self.need(lh * len(lines))
        self._draw_lines(lines, ML + indent, size, color, lh)
        self.y -= after

    def h1(self, number: str, title: str, lead: str | None = None):
        if self.y < H - TOP - 0.01:            # not at the top of a page: leave a gap, or start a new page
            self.y -= 0.35
            if self.y - 3.0 < BOTTOM:
                self.new_page()
        self.y -= 0.05
        self.fig.add_artist(Rectangle((ML / W, (self.y - 0.34) / H), 0.06 / W, 0.34 / H,
                                      facecolor=GREEN, edgecolor="none"))
        self.fig.text((ML + 0.16) / W, (self.y - 0.28) / H, f"{number}  {title}", fontsize=17,
                      fontweight="bold", color=INK, family=FONT)
        self.y -= 0.52
        if lead:
            self.text(lead, size=10.5, color=INK2, after=0.14)

    def h2(self, title: str):
        self.need(1.2)                         # keep a heading with at least a few lines of what follows
        self.y -= 0.1
        self.text(f"**{title}**", size=11.5, after=0.05)

    def bullets(self, items: list[str], size: float = 9.2, indent: float = 0.0):
        for it in items:
            lines = layout(it, size, CW - indent - 0.2)
            lh = size * 1.4 / 72
            self.need(lh * len(lines))
            self.fig.text((ML + indent + 0.04) / W, (self.y - lh) / H, "•", fontsize=size,
                          color=GREEN, family=FONT, va="baseline", fontweight="bold")
            self._draw_lines(lines, ML + indent + 0.2, size, INK, lh)
            self.y -= 0.035
        self.y -= 0.05

    def callout(self, s: str, size: float = 9.5, fill: str = CARD_BG, bar: str = GREEN):
        pad = 0.14
        lines = layout(s, size, CW - 2 * pad - 0.06)
        lh = size * 1.45 / 72
        h = lh * len(lines) + 2 * pad - 0.02
        self.need(h + 0.1)
        top = self.y
        self.fig.add_artist(FancyBboxPatch((ML / W, (top - h) / H), CW / W, h / H,
                                           boxstyle="round,pad=0,rounding_size=0.006",
                                           facecolor=fill, edgecolor="none", zorder=0))
        self.fig.add_artist(Rectangle((ML / W, (top - h) / H), 0.05 / W, h / H,
                                      facecolor=bar, edgecolor="none"))
        self.y -= pad - 0.03
        self._draw_lines(lines, ML + pad + 0.06, size, INK, lh)
        self.y = top - h - 0.14

    def table(self, header: list[str], rows: list[list[str]], widths: list[float],
              aligns: list[str] | None = None, size: float = 8.5, after: float = 0.16,
              bold_first_col: bool = False):
        aligns = aligns or ["left"] * len(header)
        tot = sum(widths)
        cols = [w / tot * CW for w in widths]
        pad, lh = 0.045, size * 1.38 / 72

        def cells(row, header_row=False):
            out = []
            for j, (c, cw) in enumerate(zip(row, cols)):
                txt = f"**{c}**" if (header_row or (bold_first_col and j == 0)) and c and "**" not in c else c
                out.append(layout(txt, size, cw - 2 * pad))
            return out

        def draw_row(row, header_row=False):
            cl = cells(row, header_row)
            n = max(len(x) for x in cl)
            h = n * lh + 2 * pad
            self.need(h)
            top = self.y
            if header_row:
                self.fig.add_artist(Rectangle((ML / W, (top - h) / H), CW / W, h / H,
                                              facecolor=PILL_BG, edgecolor="none"))
            x = ML
            for j, (lines, cw) in enumerate(zip(cl, cols)):
                yy = top - pad
                for line in lines:
                    yy -= lh
                    cx = x + cw - pad - line_w(line, size) if aligns[j] == "right" else x + pad
                    draw_line(self.fig, line, cx, yy + 0.02, size, INK2 if header_row else INK)
                x += cw
            self.y = top - h
            self.fig.add_artist(Line2D([ML / W, (ML + CW) / W], [self.y / H] * 2, color=GRID, lw=0.6))

        draw_row(header, True)
        for r in rows:
            draw_row(r)
        self.y -= after

    def axes(self, h: float, left: float = 0.0, width: float | None = None, after: float = 0.18,
             title: str | None = None):
        self.need(h + (0.3 if title else 0))
        if title:
            self.text(title, size=8.5, color=INK2, after=0.06)
        ax = self.fig.add_axes([(ML + left) / W, (self.y - h) / H, (width or CW - left) / W, h / H])
        self.y -= h + after
        return ax

    def cards(self, items: list[tuple[str, str, str]], h: float = 0.95):
        """Row of number cards: (label, value, sub)."""
        self.need(h)
        n, g = len(items), 0.14
        cw = (CW - g * (n - 1)) / n
        top = self.y
        for i, (label, value, sub) in enumerate(items):
            x = ML + i * (cw + g)
            self.fig.add_artist(FancyBboxPatch((x / W, (top - h) / H), cw / W, h / H,
                                               boxstyle="round,pad=0,rounding_size=0.01",
                                               facecolor=CARD_BG, edgecolor="none"))
            self.fig.text((x + 0.14) / W, (top - 0.26) / H, label, fontsize=8, color=INK2, family=FONT)
            self.fig.text((x + 0.14) / W, (top - 0.60) / H, value, fontsize=19, fontweight="bold",
                          color=INK, family=FONT)
            self.fig.text((x + 0.14) / W, (top - 0.82) / H, sub, fontsize=7.5, color=MUTED, family=FONT)
        self.y = top - h - 0.2


def style(ax, grid_axis="y"):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(BASELINE)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=7.5, length=0)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def pct(x, nd=1, signed=False):
    s = f"{abs(x):.{nd}f}%"
    if x < 0:
        return "−" + s
    return ("+" + s) if signed else s


# ============================================================================ content
def load_monthly() -> pd.DataFrame:
    p = pd.read_csv(ROOT / "backtest" / "results" / "monthly_live.csv", parse_dates=["entry", "exit"])
    return p


def cover(doc: Doc):
    doc.new_page(cover=True)
    f = doc.fig
    f.add_artist(Rectangle((0, (H - 0.22) / H), 1, 0.22 / H, facecolor=GREEN, edgecolor="none"))
    f.text(ML / W, (H - 0.75) / H, "STRATEGY HANDBOOK", fontsize=9, color=GREEN, fontweight="bold",
           family=FONT)
    f.text(ML / W, (H - 1.45) / H, "Core & Shield", fontsize=38, fontweight="bold", color=INK, family=FONT)
    f.text(ML / W, (H - 1.9) / H, "How it works, why it exists, and how to judge it", fontsize=13,
           color=INK2, family=FONT)
    f.text(ML / W, (H - 2.2) / H, f"Version {VERSION} · {VERSION_DATE} · written before the first trade "
           "(1 October 2026)", fontsize=8.5, color=MUTED, family=FONT)
    doc.y = H - 2.55
    doc.callout("**In one sentence:** half the money sits in a classic 60/40 (the **Core**), the other half is "
                "run by a rules-based model (the **Shield**) that each month picks the strongest, calmest and "
                "least-crowded of 12 ETFs, or retreats to cash. The goal is roughly a 60/40's return with much "
                "smaller losses when markets fall.", size=10.5)

    # structure donut
    ax = f.add_axes([ML / W, (doc.y - 3.3) / H, 3.3 / W, 3.3 / H])
    inner = [50, 50]
    ax.pie(inner, radius=0.62, colors=[BLUE, GREEN], startangle=90, counterclock=False,
           wedgeprops=dict(width=0.26, edgecolor=SURFACE, linewidth=2))
    outer = [30, 20] + [10] * 5
    oc = [BLUE, BLUE_L] + [GREEN] * 5
    wedges, _ = ax.pie(outer, radius=1.0, colors=oc, startangle=90, counterclock=False,
                       wedgeprops=dict(width=0.3, edgecolor=SURFACE, linewidth=2))
    for w_, a in zip(wedges[2:], (1.0, 0.85, 0.7, 0.55, 0.4)):
        w_.set_alpha(a)
    ax.text(0, 0.08, "100%", ha="center", va="center", fontsize=13, fontweight="bold", family=FONT)
    ax.text(0, -0.12, "portfolio", ha="center", va="center", fontsize=8, color=MUTED, family=FONT)
    ax.set_aspect("equal")
    lx = ML + 3.6
    ly = doc.y - 0.35
    legend = [(BLUE, "**Core · 50%** · fixed, never changes"),
              (BLUE, "SPY 30% · US stocks (S&P 500)"),
              (BLUE_L, "AGG 20% · US bonds"),
              (GREEN, "**Shield · 50%** · RAAM, re-picked monthly"),
              (GREEN, "5 slots × 10% each, chosen from 12 ETFs"),
              (GREEN, "a slot goes to cash (BIL) if its ETF is weaker than cash"),
              (GREEN, "Bitcoin (IBIT) never more than 5% of the whole portfolio")]
    for i, (c, s) in enumerate(legend):
        yy = ly - i * 0.34 - (0.12 if i >= 3 else 0)
        f.add_artist(Rectangle((lx / W, (yy - 0.02) / H), 0.13 / W, 0.13 / H, facecolor=c, edgecolor="none",
                               alpha=1.0 if "**" in s else 0.55))
        draw_line(f, parse(s), lx + 0.24, yy, 8.8, INK2, bold_color=INK)
    doc.y -= 3.55
    doc.text("**Backtest, Feb 2015 – Sep 2026, after trading costs** (Bitcoin before 2024 simulated; see section 6)",
             size=9, color=INK2, after=0.12)
    doc.cards([("Return per year", "9.3%", "60/40: 9.2%"),
               ("Sharpe vs T-bills", "0.93", "60/40: 0.73"),
               ("Worst month-end drop", "−11.1%", "60/40: −19.2%"),
               ("2022 (bear market)", "−8.8%", "60/40: −15.2%")])
    doc.table(["At a glance", ""],
              [["Account", "Alpaca paper trading account, starting value $100,000 (move to IBKR paper planned)"],
               ["Trades", "Once a month: signal after the last trading day's close, orders the next morning"],
               ["Run by", "Claude Code cloud routines; the maths and orders are a fixed Python script"],
               ["Alerts", "Discord: daily health line, monthly PDF report, any halt"],
               ["Status", "Locked for evaluation from 24 Sep 2026; judged against 60/40 at 1, 3, 6 and 12 months"]],
              [1.2, 5], bold_first_col=True, size=8.5)


def section_idea(doc: Doc):
    doc.new_page()
    doc.h1("1", "The idea", "Why this strategy exists, where it comes from, and what it is (and isn't) for.")
    doc.h2("The problem it solves")
    doc.text("A 60/40 portfolio is the standard balanced benchmark, but its losses in a bad year are large: "
             "**−15% in 2022** and about **−19%** at its worst month-end in our test window. Tactical rotation "
             "models are the opposite: they sidestep much of a slow bear market by moving into bonds or cash, "
             "but they lag badly in strong bull markets because they hold defensive assets too often.")
    doc.text("Core & Shield combines the two. The **Core** is a fixed 60/40 that captures most of the market's "
             "long-run growth. The **Shield** is a rotation model that behaves like a shock absorber. Together "
             "they aim for **about the same return as a 60/40, with roughly half the damage in bear markets**.")
    doc.h2("Where it comes from")
    doc.text("The Shield is the **Ranked Asset Allocation Model (RAAM)** by Gioele Giordano, which won the 2018 "
             "Charles H. Dow Award from the CMT Association. RAAM ranks a diversified set of ETFs on momentum, "
             "volatility and correlation each month and holds the best five, moving to cash when nothing is "
             "trending up.")
    doc.text("Our version is **not** the paper's version. The paper's headline (+638%, Sharpe 1.94 over 2004–17) "
             "was in-sample, before costs, and could not be reproduced. We resolved the paper's seven ambiguities, "
             "made three safety upgrades, removed a factor that hurt results, wrapped it in the Core, and added a "
             "small, capped Bitcoin sleeve. Section 9 lists every change and the evidence behind it.")
    doc.h2("What it is designed to do")
    doc.bullets(["**Specialise in defence.** It wins mainly by losing less, not by making more. Its best years "
                 "relative to 60/40 are bad years for markets (2018 aside, see section 6).",
                 "**Stay invested for growth.** Half the portfolio is always in stocks and bonds, so it does not "
                 "miss recoveries the way a pure timing model can.",
                 "**Follow rules, not opinions.** The allocation is computed by a script. Nobody, including Claude, "
                 "overrides it because of news or a market view.",
                 "**Trade rarely.** One rebalance a month, about 15% of the portfolio turned over each time."])
    doc.h2("What it is not")
    doc.bullets(["**Not a way to beat the S&P 500.** In a strong bull market it will trail SPY, often by a lot, "
                 "and usually trail 60/40 a little. That is by design.",
                 "**Not a crash-proof product.** A sudden one-day crash hits before any monthly model can react; "
                 "the circuit breaker limits the damage but cannot prevent it.",
                 "**Not a Bitcoin strategy.** Bitcoin is one candidate of twelve and is capped at 5%."])
    doc.h2("Who a strategy like this suits")
    doc.text("Investors who care more about the size of the worst loss than about maximum return: people drawing "
             "an income, those near a goal date, and institutions such as pension and superannuation funds that "
             "are judged on risk-adjusted returns. For them, matching a 60/40's return with a much smaller drawdown "
             "is a meaningful improvement.")
    doc.callout("**Its personality in one line:** a balanced portfolio that expects to be roughly level with 60/40 "
                "in good years and clearly ahead in bad ones.")


def section_build(doc: Doc):
    doc.h1("2", "How the portfolio is built", "Two halves, 13 possible holdings, one cap.")
    doc.table(["Half", "Weight", "Holdings", "How it changes"],
              [["Core", "50%", "SPY 30% + AGG 20%", "Never. Reset to exactly these weights at every monthly rebalance."],
               ["Shield", "50%", "5 slots of 10% each, from 12 candidate ETFs, with BIL (cash) for failed slots",
                "Re-chosen every month by the RAAM rules in section 3."]],
              [0.8, 0.7, 2.2, 2.6], bold_first_col=True)
    doc.text("The two halves simply add up. If the Shield picks AGG, the portfolio holds 20% (Core) + 10% "
             "(Shield) = **30% AGG**. If the Shield sends a slot to cash, that 10% sits in BIL, a 1–3 month "
             "Treasury bill fund that earns the short-term interest rate.")
    doc.h2("The Shield's 12 candidates")
    doc.text("Eleven ETFs from Craig Israelsen's **7Twelve** diversified portfolio, plus spot Bitcoin. Together they "
             "span stocks, real estate, commodities, bonds and crypto, so there is usually something trending up.",
             after=0.12)
    doc.table(["Asset class", "ETF", "What it holds"],
              [["US stocks", "VV", "Vanguard Large-Cap: large US companies"],
               ["", "IJH", "iShares Core S&P Mid-Cap: mid-sized US companies"],
               ["", "IJR", "iShares Core S&P Small-Cap: small US companies"],
               ["International stocks", "EFA", "iShares MSCI EAFE: developed markets outside North America"],
               ["", "EEM", "iShares MSCI Emerging Markets"],
               ["Real estate", "RWR", "SPDR Dow Jones REIT: US real estate investment trusts"],
               ["Commodities / resources", "DBC", "Invesco DB Commodity Index: energy, metals, agriculture"],
               ["", "VAW", "Vanguard Materials: mining, chemicals and materials companies"],
               ["US bonds", "AGG", "iShares Core US Aggregate Bond: the broad US bond market"],
               ["", "TIP", "iShares TIPS: inflation-protected US Treasuries"],
               ["International bonds", "IGOV", "iShares International Treasury: developed-market government bonds"],
               ["Crypto", "IBIT", "iShares Bitcoin Trust: spot Bitcoin. **Capped at 5% of the portfolio**"],
               ["Cash (not ranked)", "BIL", "SPDR 1–3 Month T-Bill: where failed slots and any IBIT excess go"],
               ["Core only", "SPY", "SPDR S&P 500: the Core's stock holding (not a Shield candidate)"]],
              [1.5, 0.6, 4.2], size=8.3)
    doc.h2("The Bitcoin cap")
    doc.text("A normal Shield slot is 10% of the portfolio. If IBIT is picked, it only gets **5%**; the other 5% "
             "goes to BIL. The cap is enforced by the script after the ranking, so the portfolio never starts a "
             "month with more than 5% in Bitcoin (between rebalances it drifts with Bitcoin's price). A Bitcoin "
             "crash of −80% while it is held costs roughly 3–4% of the portfolio.")
    p = [("AGG", 100), ("SPY", 100), ("BIL", 87.9), ("TIP", 59.3), ("IBIT", 52.1), ("DBC", 40.7), ("IGOV", 35.7),
         ("RWR", 33.6), ("VV", 33.6), ("IJR", 14.3), ("EEM", 12.9), ("VAW", 10.0), ("EFA", 10.0), ("IJH", 4.3)]
    doc.need(2.6)
    doc.h2("How often each ETF was held (backtest, % of months)")
    ax = doc.axes(2.0)
    style(ax, "x")
    names, vals = [x[0] for x in p][::-1], [x[1] for x in p][::-1]
    cols = [BLUE if n in ("SPY", "AGG") else (MUTED if n == "BIL" else GREEN) for n in names]
    ax.barh(names, vals, color=cols, height=0.62)
    for i, v in enumerate(vals):
        ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=7, color=INK2, family=FONT)
    ax.set_xlim(0, 112)
    ax.set_xticks([])
    ax.tick_params(axis="y", labelsize=7.5, colors=INK2)
    ax.spines["bottom"].set_visible(False)
    doc.text("Blue = always held through the Core. Grey = cash. SPY and AGG show 100% because the Core always "
             "holds them; the Shield also picks AGG in some months.", size=8, color=MUTED)


def flow(ax):
    ax.axis("off")
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 2)
    steps = [("1  Measure", "M, V, C for all 12\nETFs at month-end"),
             ("2  Rank", "1 (best) to 12\non each factor"),
             ("3  Score", "average of the\nthree ranks"),
             ("4  Pick 5", "the five lowest\nscores, 10% each"),
             ("5  Cash test", "a pick weaker than\ncash goes to BIL"),
             ("6  Add the Core", "+ SPY 30%\n+ AGG 20%"),
             ("7  Cap Bitcoin", "IBIT ≤ 5%,\nexcess to BIL"),
             ("8  Trade", "next morning, then\nhold all month")]
    for i, (t, s) in enumerate(steps):
        r, c = divmod(i, 4)
        x, y = c + 0.06, 1.08 - r * 1.02
        ax.add_patch(FancyBboxPatch((x, y), 0.86, 0.8, boxstyle="round,pad=0,rounding_size=0.06",
                                    facecolor=CARD_BG if i != 7 else GREEN, edgecolor="none"))
        ax.text(x + 0.08, y + 0.6, t, fontsize=8.8, fontweight="bold", family=FONT,
                color=INK if i != 7 else "white")
        ax.text(x + 0.08, y + 0.44, s, fontsize=7.6, family=FONT, va="top",
                color=INK2 if i != 7 else "white", linespacing=1.35)
        if c < 3:
            ax.annotate("", xy=(x + 0.95, y + 0.4), xytext=(x + 0.87, y + 0.4),
                        arrowprops=dict(arrowstyle="-|>", color=BASELINE, lw=1))


def section_rules(doc: Doc):
    doc.h1("3", "The monthly decision", "Eight mechanical steps, computed by the script after the last trading "
           "day's close.")
    flow(doc.axes(2.0, after=0.2))
    doc.h2("The three factors")
    doc.table(["Factor", "Measured as", "Best rank goes to", "Why it matters"],
              [["M · Momentum", "Price change over the last 84 trading days (about 4 months)", "Highest momentum",
                "Assets that have been rising tend to keep rising for a while"],
               ["V · Volatility", "Daily price swings (EWMA, λ = 0.94, annualised, smoothed over 10 days)",
                "Lowest volatility", "Calmer assets give smoother returns and smaller losses"],
               ["C · Correlation", "Average correlation of daily returns with the other 11 candidates over 84 days",
                "Lowest correlation", "Assets that move differently add real diversification"]],
              [1.1, 2.3, 1.2, 2.2], size=8.3, bold_first_col=True)
    doc.h2("Score and selection")
    doc.callout("**Score = ⅓ × Rank(M) + ⅓ × Rank(V) + ⅓ × Rank(C) − Momentum ÷ 1000**     (lower is better)\n",
                fill=PILL_BG)
    doc.bullets(["Each candidate is ranked 1 (best) to 12 on each factor; ties share the average rank.",
                 "The tiny momentum term only breaks exact ties, in favour of the stronger trend.",
                 "The **five lowest scores** are picked. Each gets 20% of the Shield, which is 10% of the portfolio.",
                 "**Cash test:** a pick keeps its slot only if its 84-day momentum beats cash's own (BIL's) "
                 "84-day momentum. Otherwise that slot goes to BIL. If nothing beats cash, the whole Shield "
                 "(50%) sits in BIL while the Core stays invested.",
                 "A fourth factor from the paper (an ATR trend/breakout signal) is still calculated and logged, "
                 "but **no longer scored**: three separate backtests showed results were better without it."])
    doc.h2("Worked example (illustrative numbers)")
    doc.text("Suppose the five lowest scores are TIP, IBIT, DBC, AGG and VV, cash momentum is +1.3%, and VV's "
             "momentum is −1.0%:", after=0.1)
    doc.table(["Step", "SPY", "AGG", "TIP", "DBC", "IBIT", "VV", "BIL", "Total"],
              [["Shield picks (10% each)", "", "10%", "10%", "10%", "10%", "10%", "", "50%"],
               ["Cash test: VV −1.0% < cash +1.3%", "", "10%", "10%", "10%", "10%", "0%", "10%", "50%"],
               ["Add the Core", "30%", "30%", "10%", "10%", "10%", "", "10%", "100%"],
               ["Cap IBIT at 5%", "30%", "30%", "10%", "10%", "**5%**", "", "**15%**", "100%"]],
              [2.6, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.6],
              aligns=["left"] + ["right"] * 8, size=8.2)
    doc.text("The last row is what gets bought on the first trading day and held for the month.", size=8.5,
             color=MUTED)


def section_ops(doc: Doc):
    doc.h1("4", "Timing and operations", "Who does what, and when. Everything runs in the cloud; the GitHub "
           "repository is the system's memory.")
    doc.h2("A month in the life")
    doc.table(["When (US Eastern)", "What happens"],
              [["Every weekday after the close (17:30 summer / 16:30 winter)",
                "Health check: account value, drawdown, positions vs targets, circuit breaker. One Discord line."],
               ["Last trading day, after the close",
                "Research scan first (context only), then the **signal** is computed and saved. Pre-flight check "
                "that every ETF is tradable."],
               ["Last trading day, 19:00 summer / 18:00 winter",
                "One-page **monthly PDF report** (account vs 60/40) posted to Discord."],
               ["First trading day, 10:45 summer / 09:45 winter",
                "**Rebalance:** sells first, then buys, as market orders using fractional shares (whole shares "
                "for any ETF that can't be fractional). Fills and slippage logged."],
               ["First trading day, after the close", "**Monthly review** against the evaluation scorecard."],
               ["Rest of the month", "Nothing. No stops, no intra-month trades, no reacting to news."]],
              [2.2, 4.4], size=8.4, bold_first_col=False)
    doc.text("Routine schedules are stored in UTC, so clock times shift by an hour when US daylight saving ends "
             "or starts. Both versions are safely after the open or the close. Holidays are handled by Alpaca's "
             "market calendar.", size=8.5, color=MUTED)
    doc.h2("Who does what")
    doc.table(["Part", "Role"],
              [["scripts/raam.py", "All the maths, every guardrail and every order. Deterministic: same data in, "
                                   "same answer out."],
               ["Claude (cloud routines)", "**Operator, not strategist.** Runs the commands, writes the logs, does "
                                           "research for context, sends the Discord messages. It may halt if "
                                           "something looks wrong. It never changes targets, picks, timing or rules."],
               ["GitHub repository", "The only persistent memory: config, rules, signals, trade log, reports. "
                                     "Every run starts from a fresh copy and pushes its results back."],
               ["Alpaca", "Paper brokerage account and market data (a move to Interactive Brokers paper is "
                          "planned after a feasibility check)."],
               ["Discord", "Where every message, report and alert arrives."],
               ["The owner", "The only one who can change the rules, in an interactive session, with the change "
                             "and its evidence written into the change log."]],
              [1.7, 4.9], size=8.4, bold_first_col=True)
    doc.h2("Principles")
    doc.bullets(["**A missed rebalance is cheap; a wrong trade is not.** When data is stale, a fund changes, weights "
                 "don't add up or the broker errors, the system halts and alerts instead of improvising. "
                 "(Stress tests: filling up to 5 days late made no meaningful difference.)",
                 "**Research never changes the allocation.** The one exception is a structural problem with an "
                 "ETF (closure, merger, ticker change, trading halt), which is grounds to halt.",
                 "**Keys live only in the cloud environment's variables**, never in files, commits or messages."])


def section_safety(doc: Doc):
    doc.h1("5", "Safety rails", "Checks that sit outside the strategy and can only stop trading, never add risk.")
    doc.h2("Circuit breaker")
    doc.bullets(["**Trips** when the whole portfolio is **20% below its high-water mark**, or falls **5% in a "
                 "single day**.",
                 "**Action:** the next morning, everything (Core included) moves to 100% BIL.",
                 "**Re-entry:** automatic at the next monthly rebalance, following a fresh signal, with the "
                 "high-water mark reset.",
                 "**History:** never tripped in the 2015–2026 backtest (worst daily drawdown −14.1%). In the 2008 "
                 "test it tripped once (23 Feb 2009, −20.2%) and re-entered in March.",
                 "**Trade-off:** in a one-day crash it locks the loss and can miss a fast rebound until the next "
                 "month. It is a tail-risk net, not a return enhancer."])
    doc.h2("Checks before every signal and trade")
    doc.table(["Check", "If it fails"],
              [["Every ETF has a fresh price bar for the signal date", "Halt: no signal is saved"],
               ["Momentum, volatility and correlation are valid numbers", "Halt"],
               ["Target weights add up to 100% (±0.5%); none negative", "Halt"],
               ["Only universe tickers can be traded", "Halt; stray positions are left alone and flagged"],
               ["No single buy above 35% of the account", "Halt"],
               ["Account is a paper account (live needs two explicit switches)", "Refuses to run"],
               ["Market is open at order time", "Halt; nothing submitted"],
               ["Each ETF is tradable on Alpaca", "Halt; non-fractionable ETFs use whole shares"],
               ["Buys never exceed available cash", "Buys scaled down to fit"],
               ["Every order ends 'filled'", "Halt and alert, with the fills recorded"],
               ["The same month can't be traded twice", "Second run does nothing"]],
              [3.9, 2.7], size=8.4)
    doc.h2("Tested failure drills")
    doc.text("Automated tests simulate a rejected order, a partial fill, a broker outage, missing, stale and zero "
             "prices, an untradable ETF and an unexpected position. All end in a safe halt with no wrong trade. "
             "Two small gaps the drills found were fixed on 14 Oct 2026:", after=0.08)
    doc.bullets(["**F1:** if the broker fails halfway through a rebalance, the orders that already filled (and "
                 "the one that failed) are now written to the trade log, and the run halts for the owner.",
                 "**F2:** a blank or zero closing price anywhere in the lookback window now halts the signal, "
                 "instead of the ETF being ranked on the previous day's price."])


def section_results(doc: Doc, p: pd.DataFrame):
    doc.new_page()
    doc.h1("6", "Historical results", "What the rules would have done from February 2015 to September 2026.")
    doc.text("**How the test works:** the live script's own signal code, run at every month-end on Yahoo "
             "Finance adjusted prices; fills at the next day's open; 5 basis points of cost per trade; the "
             "circuit breaker checked daily. IBIT only exists from January 2024, so before that it is simulated "
             "from the Bitcoin price minus IBIT's 0.25% fee. Past results do not guarantee future results.",
             size=8.8, color=INK2)
    x = p["exit"]
    ax = doc.axes(2.05, after=0.12, title="Growth of $100,000 (log scale)")
    style(ax)
    for col, lab, c, lw in (("spy", "SPY", BLUE_L, 1.0), ("b6040", "60/40", GREY, 1.3), ("ret", "Core & Shield", GREEN, 2.0)):
        ax.plot(x, (1 + p[col]).cumprod() * 100_000, color=c, lw=lw, label=lab)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v / 1000:,.0f}k"))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_yticks([100_000, 150_000, 200_000, 300_000, 400_000])
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", labelcolor=INK2)
    ax2 = doc.axes(1.0, title="Drawdown from peak, month-end (%)")
    style(ax2)
    for col, c, lw in (("b6040", GREY, 1.1), ("ret", GREEN, 1.6)):
        eq = (1 + p[col]).cumprod()
        dd = (eq / eq.cummax() - 1) * 100
        ax2.fill_between(x, dd, 0, color=c, alpha=0.18 if col == "ret" else 0.1, lw=0)
        ax2.plot(x, dd, color=c, lw=lw)
    doc.table(["", "Return / yr", "Sharpe", "Sortino", "Calmar", "Worst month-end", "Worst day", "2022"],
              [["**Core & Shield**", "9.3%", "0.93", "1.58", "0.84", "−11.1%", "−14.1%", "−8.8%"],
               ["60/40 (SPY/AGG)", "9.2%", "0.73", "1.11", "0.48", "−19.2%", "", "−15.2%"],
               ["SPY", "14.1%", "0.81", "1.24", "0.61", "−23.3%", "−33.7%", "−18.0%"],
               ["C&S without Bitcoin", "6.5%", "0.66", "1.00", "0.59", "−11.1%", "−14.6%", "≈ −8%"]],
              [1.75, 0.85, 0.65, 0.7, 0.65, 1.0, 0.85, 0.7], aligns=["left"] + ["right"] * 7, size=8.2, after=0.06)
    doc.text("Sharpe and Sortino measured against T-bills (2.0%/yr); at a 0% rate the Sharpe ratios are 1.18, 0.93, "
             "0.93 and 0.95. Sortino counts only downside volatility; Calmar = return ÷ worst month-end drop. "
             "2008 test (no Bitcoin): Core & Shield −7.4% vs 60/40 −17.7%.", size=8, color=MUTED)
    cy = p.assign(year=p["entry"].dt.year).groupby("year").agg(
        cs=("ret", lambda r: ((1 + r).prod() - 1) * 100), b=("b6040", lambda r: ((1 + r).prod() - 1) * 100))
    ax3 = doc.axes(1.5, after=0.1, title="Calendar-year returns (%)  · *2026 to date")
    style(ax3)
    xs = np.arange(len(cy))
    ax3.bar(xs - 0.2, cy["cs"], 0.38, color=GREEN, label="Core & Shield")
    ax3.bar(xs + 0.2, cy["b"], 0.38, color=GREY, alpha=0.7, label="60/40")
    ax3.axhline(0, color=BASELINE, lw=0.8)
    ax3.set_xticks(xs, [str(y) + ("*" if y == 2026 else "") for y in cy.index])
    for i, (a, b) in enumerate(zip(cy["cs"], cy["b"])):
        ax3.text(i - 0.2, a + (0.8 if a >= 0 else -0.8), f"{a:.0f}" if abs(a) >= 0.5 else "0", ha="center",
                 va="bottom" if a >= 0 else "top", fontsize=6.3, color=INK2, family=FONT)
    ax3.legend(frameon=False, fontsize=7.5, loc="upper right", labelcolor=INK2)
    doc.text("**Reading it:** level with 60/40 over the whole period; clearly ahead in 2017 (Bitcoin) and 2022, "
             "slightly ahead in 2020, 2021 and 2026, behind in strong equity years (2019, 2023–2025). 2018 was worse "
             "than 60/40 mostly because Bitcoin's crash hit while it was held (without Bitcoin it was about level).",
             size=8.8)


def section_stress(doc: Doc, p: pd.DataFrame):
    doc.new_page()
    doc.h1("7", "Stress tests", "How fragile is the result? Run 27 Sep 2026 with backtest/stress.py; none of it "
           "changed the strategy.")
    doc.table(["Test", "What was tried", "Result"],
              [["Trading costs", "5, 10, 25, 50 bps per trade",
                "Risk-adjusted edge survives even 50 bps (Sharpe 0.97 vs about 0.92). The return edge disappears "
                "above about 10 bps."],
               ["Settings", "13 nearby settings: lookbacks 63–126 days, hold 4 or 6, λ 0.92/0.97, each weight ±10 pp",
                "**13 of 13** still beat 60/40's Sharpe (range 1.03–1.28). Not a lucky peak."],
               ["Late fills", "Trade 2, 3 or 5 days after the signal", "No real difference (Sharpe 1.18–1.23)."],
               ["Any single year", "127 rolling 12-month windows",
                "Beat 60/40 on return in only **49%**, but had the **smaller drawdown in 89%**, and did better in "
                "93% of the windows where 60/40 lost money."],
               ["Monte Carlo", "5,000 simulated 10-year paths (6-month blocks of history)",
                "**94%** chance of a higher Sharpe than 60/40, **97%** of a smaller worst drop. Any single year: "
                "52% chance of trailing 60/40, 14% chance of a loss."]],
              [1.1, 2.4, 3.1], size=8.3, bold_first_col=True)
    doc.need(3.3)
    doc.h2("Shocks worse than anything in the test window")
    doc.text("Each made-up shock was injected into real prices at six different dates and the whole model re-run, "
             "so it reacts as it would live. Averages shown; real 2008 and 2022 added for comparison.", size=8.8,
             color=INK2)
    rows = [("2022 (real)", -8.8, -15.2), ("2008 (real, no Bitcoin)", -7.4, -17.7),
            ("Stagflation, 6 months", -5.9, -17.3), ("Stocks & bonds fall together, 6 mo", -10.3, -22.3),
            ("Crash day −20%", -9.3, -16.2)]
    ax = doc.axes(2.1, after=0.1, left=2.0)
    style(ax, "x")
    ys = np.arange(len(rows))
    ax.barh(ys + 0.19, [r[1] for r in rows], 0.36, color=GREEN, label="Core & Shield")
    ax.barh(ys - 0.19, [r[2] for r in rows], 0.36, color=GREY, alpha=0.7, label="60/40")
    for i, r in enumerate(rows):
        ax.text(r[1] - 0.4, i + 0.19, pct(r[1]), va="center", ha="right", fontsize=7, color=INK2, family=FONT)
        ax.text(r[2] - 0.4, i - 0.19, pct(r[2]), va="center", ha="right", fontsize=7, color=INK2, family=FONT)
    ax.set_yticks(ys, [r[0] for r in rows])
    ax.set_xlim(-27, 0)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: pct(v, 0)))
    ax.legend(frameon=False, fontsize=7.5, loc="lower left", labelcolor=INK2)
    ax.tick_params(axis="y", labelsize=7.8, colors=INK2)
    doc.bullets(["Core & Shield took **34–57% of 60/40's loss** in every made-up shock.",
                 "**Crash day:** the −5% daily breaker trips every time, so the portfolio sits in cash until "
                 "the next rebalance and can miss a quick rebound.",
                 "**Realistic worst case:** a six-month stock-and-bond slide running straight into a Covid-style "
                 "crash reached **−21%** and tripped the −20% breaker. That is deeper than anything in the "
                 "backtest (−14.1%), so plan for a 20% drawdown being possible.",
                 "**Bitcoin −80% while held:** about 3 percentage points extra loss, as the 5% cap intends."],
                size=9)
    r12 = ((1 + p["ret"]).rolling(12).apply(np.prod, raw=True) - (1 + p["b6040"]).rolling(12).apply(np.prod, raw=True)) * 100
    ax2 = doc.axes(1.35, after=0.2, title="Trailing 12-month return minus 60/40 (percentage points)")
    style(ax2)
    ax2.bar(p["exit"], r12, width=25, color=np.where(r12 >= 0, GREEN, GREY), alpha=0.85)
    ax2.axhline(0, color=BASELINE, lw=0.8)
    doc.text("Green = ahead of 60/40 over the previous 12 months. Long stretches behind are normal in bull markets.",
             size=8, color=MUTED)


def section_judge(doc: Doc):
    doc.h1("8", "What to expect, and how to judge it", "The criteria were fixed before the first trade so results "
           "can't move the goalposts.")
    doc.h2("Strengths and weaknesses")
    doc.table(["Good at", "Weak at"],
              [["Slow bear markets and rising-rate years (2022: −8.8% vs −15.2%)",
                "Strong equity bull markets: it trails SPY by a lot and 60/40 by a little"],
               ["Smaller drawdowns in almost every period (89% of rolling years)",
                "Sudden one-day crashes: a monthly model can't react in time"],
               ["Robust to costs, settings and late trades",
                "Return edge over 60/40 is thin; about half of it depends on Bitcoin"],
               ["Simple, transparent, rules-based, low turnover",
                "Single years are a coin flip against 60/40 on return"]],
              [3.3, 3.3], size=8.5)
    doc.h2("Normal ranges (from the backtest) for judging a live month")
    doc.table(["Measure", "Normal", "Unusual / investigate"],
              [["Monthly return", "Between −3% and +3% (78% of months); 65% of months positive",
                "Outside −5.7% to +6.9%"],
               ["Cash (BIL) weight", "About 16% on average; about 37% in a year like 2022", "Above 50%"],
               ["Drawdown from peak", "Up to about −11% month-end, −14% daily", "Worse than −14.1%"],
               ["Share of 60/40's loss in its down months", "About 63%", "Above 85% on average"],
               ["Bitcoin (IBIT)", "Held in about half of months, at 5%", "Above 5% at a rebalance"],
               ["Turnover", "About 15% of the portfolio per month", "—"]],
              [1.9, 2.9, 1.8], size=8.3, bold_first_col=True)
    doc.h2("Checkpoints")
    doc.table(["When", "Question", "Passes when"],
              [["1 month (early Nov 2026)", "Does it run?", "All operations criteria pass for October: signal and "
                "rebalance on time, all orders filled, slippage ≤ 10 bps, holdings within ±2 pp of target, "
                "IBIT ≤ 5%, report delivered"],
               ["3 months (early Jan 2027)", "Is it reliable?", "Operations pass 3 months out of 3; returns, cash "
                "and drawdown inside the normal ranges"],
               ["6 months (early Apr 2027)", "Does it behave as designed?", "Live returns match a backtest of the "
                "same months within 0.3 pp a month; defence assessed if 60/40 had 2+ down months"],
               ["12 months (early Oct 2027)", "Is it worth running?", "See the verdict rules below"]],
              [1.7, 1.6, 3.3], size=8.3, bold_first_col=True)
    doc.h2("The 12-month verdict")
    doc.bullets(["**Working as designed:** operations pass in 11+ months, behaviour matches the backtest, and the "
                 "12-month drawdown is smaller than 60/40's (plus the down-month test, if 60/40 had 2+ down months).",
                 "**Inconclusive:** everything passes but 60/40 had fewer than 2 down months. Normal in a calm year; "
                 "the defence hasn't been tested yet. Keep running.",
                 "**Not working:** the live account doesn't match the model, or it takes more than 100% of 60/40's "
                 "losses, or its drawdown is larger than 60/40's in a year when 60/40 fell.",
                 "**Explicitly not a failure:** trailing SPY, or trailing 60/40 in a year when 60/40 rose."])
    doc.callout("**Rule for the evaluation year:** don't change the strategy unless something is broken. A change "
                "resets the evidence. Ideas are parked and tested as fixed variants at the 6-month checkpoint.")


def section_history(doc: Doc):
    doc.h1("9", "Decision history", "How the strategy got here, including what was tried and rejected.")
    doc.table(["Date", "Decision", "Evidence"],
              [["23 Sep 2026", "Set up pure RAAM from the paper, with defaults for its 7 ambiguities",
                "Paper's +638% claim could not be reproduced"],
               ["23 Sep 2026", "**Tier 1 upgrades:** cash test uses BIL's momentum (was > 0%); BIL replaces SHY as "
                               "cash; breaker at −20% with automatic re-entry (was −15%, manual)",
                "Safer behaviour at little cost"],
               ["23 Sep 2026", "**Trend factor removed** from the score", "Three backtests agreed: better return, "
                               "smaller drawdown, in both halves of the period"],
               ["24 Sep 2026", "**Core & Shield:** 50% fixed 60/40 + 50% RAAM", "RAAM alone lagged badly in bull "
                               "markets; the blend matched 60/40's Sharpe with far smaller drawdowns"],
               ["24 Sep 2026", "Strategy locked for a 12-month paper evaluation", "Owner decision"],
               ["Sep 2026", "Trade the morning after the signal (10:45 ET summer / 09:45 winter)",
                "Month-end close, first day and mid-month compared; no major downside to keeping it"],
               ["26 Sep 2026", "**IBIT added**, capped at 5% of the portfolio", "Return 6.5% → 9.3%, Sharpe "
                               "0.95 → 1.18, worst drop slightly better; better in every sub-period; about half the "
                               "gain survives with Bitcoin's long-run return flattened to 0%"],
               ["26 Sep 2026", "Evaluation criteria written and fixed", "Before any live result existed"],
               ["27 Sep 2026", "Stress tests run (section 7)", "Robust to costs, settings and timing; worst case "
                               "about −21%"]],
              [0.95, 3.0, 2.65], size=8.1)
    doc.h2("Tested and rejected, or parked")
    doc.table(["Idea", "Verdict", "Why"],
              [["Swap VV→TLT and VAW→GLD (crisis assets)", "Rejected", "Better before 2020, worse after; made March "
                                                                     "2020 and 2008 worse"],
               ["Correlation measured against the Core too", "Rejected", "Worse from 2020 onward"],
               ["Size positions by inverse volatility", "Rejected", "Failed from 2020 onward"],
               ["Heavier momentum weight", "Not recommended", "Trades defence for return"],
               ["Bitcoin uncapped (10% slots)", "Not adopted", "12.7%/yr but more dependent on Bitcoin"],
               ["Volatility-managed Core", "Parked", "Shallower losses in every crisis, same Sharpe, "
                                                     "about 0.7%/yr less return"],
               ["Risk-based sizing, staggered rebalancing", "Parked", "Candidates for the 6-month checkpoint"]],
              [2.3, 1.1, 3.2], size=8.3, bold_first_col=True)
    doc.h2("Honest assessment at launch")
    doc.text("Rated about **70/100** before the first trade: a sound, defensive, well-guarded balanced strategy "
             "with a thin return edge over 60/40, a real but modest dependence on Bitcoin, and no live track record "
             "yet. About 11 years of data means a Sharpe estimate is only accurate to roughly ±0.3, so most "
             "differences between variants are not statistically significant. The live year is what decides it.")
    doc.h2("Glossary")
    doc.table(["Term", "Meaning"],
              [["60/40", "60% US stocks (SPY) + 40% US bonds (AGG): the benchmark"],
               ["Sharpe ratio", "Return per unit of volatility; higher is better. 1.0+ is good for a balanced fund"],
               ["Drawdown", "Fall from the highest value reached so far"],
               ["Momentum", "How much a price has changed over a lookback period (here about 4 months)"],
               ["Basis point (bp)", "0.01%. 10 bps = 0.1%"],
               ["Slippage", "Difference between the price when an order was planned and the price it filled at"],
               ["Circuit breaker", "Automatic move to cash after a −20% drawdown or −5% day"],
               ["High-water mark", "The highest account value so far, used to measure drawdown"]],
              [1.5, 5.1], size=8.3, bold_first_col=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "Core-and-Shield-Strategy.pdf"))
    ap.add_argument("--png-dir", help="also save each page as a PNG here (for checking the layout)")
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    p = load_monthly()
    with PdfPages(out, metadata={"Title": "Core & Shield: Strategy Handbook", "Author": "Core & Shield bot",
                                 "Subject": f"Version {VERSION}, {VERSION_DATE}"}) as pdf:
        png = pathlib.Path(args.png_dir) if args.png_dir else None
        if png:
            png.mkdir(parents=True, exist_ok=True)
        doc = Doc(pdf, png)
        cover(doc)
        section_idea(doc)
        section_build(doc)
        section_rules(doc)
        section_ops(doc)
        section_safety(doc)
        section_results(doc, p)
        section_stress(doc, p)
        section_judge(doc)
        section_history(doc)
        doc.finish()
        pages = doc.page
    print(out, out.stat().st_size, "bytes,", pages, "pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
