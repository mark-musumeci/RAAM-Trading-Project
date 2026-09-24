#!/usr/bin/env python3
"""RAAM engine - Core & Shield: a fixed 60/40 Core plus the Ranked Asset Allocation Model
(Giordano, 2018 Dow Award) as the Shield.

Deterministic core used by the Claude Code routines. Claude orchestrates; this
script does all math, guardrail checks and order execution.

Subcommands (all print a single JSON object to stdout):
  calendar   [--date D]                     trading-day facts for D (default: today ET)
  signal     [--date D] [--force] [--dry-run]   month-end factors, ranks, target weights
  rebalance  [--date D] [--force] [--dry-run]   execute last month's signal (1st trading day)
  health     [--dry-run]                    equity, drawdown, circuit breaker, drift
  review     [--month YYYY-MM] [--force]    month performance vs 60/40, 30/70, SPY and equal-weight 7Twelve

Exit codes: 0 = ok/noop, 2 = halted by a guard (see "reason"), 1 = unexpected error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import pathlib
import sys
import time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "raam.json"
MEMORY = ROOT / "memory"
SIGNALS_DIR = MEMORY / "signals"
STATE_PATH = MEMORY / "state.json"
SIGNAL_LOG = MEMORY / "SIGNAL-LOG.md"
TRADE_LOG = MEMORY / "TRADE-LOG.md"
ET = ZoneInfo("America/New_York")
SEVEN_TWELVE_CASH = "SHY"   # benchmark only; RAAM's own cash asset comes from config


class Halt(Exception):
    """A guardrail stopped the run. Message is reported to the user."""


# --------------------------------------------------------------------------
# Environment / config / state
# --------------------------------------------------------------------------
def load_env() -> None:
    """API keys come from environment variables. In cloud routines (CLAUDE_CODE_REMOTE=true)
    .env is never read; locally it only fills variables that are not already set."""
    if os.environ.get("CLAUDE_CODE_REMOTE") == "true":
        return
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_config(path: pathlib.Path = CONFIG_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


DEFAULT_STATE = {
    "high_water_mark": None,
    "circuit_breaker": {"tripped": False, "reason": None, "tripped_on": None},
    "last_health": None,
    "equity_history": [],
}


def load_state() -> dict:
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        for k, v in DEFAULT_STATE.items():
            state.setdefault(k, v)
        return state
    return json.loads(json.dumps(DEFAULT_STATE))


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def today_et() -> dt.date:
    return dt.datetime.now(ET).date()


def month_key(d: dt.date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def prev_month_key(d: dt.date) -> str:
    first = d.replace(day=1)
    return month_key(first - dt.timedelta(days=1))


def next_month_key(d: dt.date) -> str:
    return month_key((d.replace(day=28) + dt.timedelta(days=4)).replace(day=1))


# --------------------------------------------------------------------------
# Portfolio structure (Core & Shield)
# --------------------------------------------------------------------------
def portfolio_parts(cfg: dict) -> tuple[dict, float]:
    """(core weights, shield weight). Without a 'portfolio' section the bot is RAAM alone."""
    pf = cfg.get("portfolio") or {}
    core = {k: float(v) for k, v in (pf.get("core") or {}).items() if float(v) > 0}
    shield = float(pf.get("shield_weight", 1.0))
    if shield < 0 or any(v < 0 for v in core.values()) or abs(sum(core.values()) + shield - 1) > 1e-6:
        raise ValueError(f"portfolio core {core} + shield_weight {shield} must sum to 1")
    return core, shield


def tradable_symbols(cfg: dict) -> list[str]:
    """Every symbol the bot may hold: RAAM universe, its cash asset and the Core."""
    uni = cfg["universe"]
    core, _ = portfolio_parts(cfg)
    return list(dict.fromkeys(uni["risk_assets"] + [uni["cash"]] + list(core)))


def combine_targets(shield_targets: dict, cfg: dict) -> dict:
    """Portfolio targets = Core weights + shield_weight x RAAM (Shield) weights."""
    core, shield = portfolio_parts(cfg)
    out = {s: 0.0 for s in tradable_symbols(cfg)}
    for s, w in core.items():
        out[s] += w
    for s, w in shield_targets.items():
        out[s] = out.get(s, 0.0) + shield * w
    return {k: round(v, 6) for k, v in out.items()}


# --------------------------------------------------------------------------
# Indicators (pure functions - unit tested)
# --------------------------------------------------------------------------
def momentum(close: pd.Series, days: int) -> float:
    """Absolute momentum: rate of change over `days` sessions, in percent."""
    close = close.dropna()
    if len(close) <= days:
        raise Halt(f"not enough history for momentum ({len(close)} bars, need {days + 1})")
    return float((close.iloc[-1] / close.iloc[-1 - days] - 1.0) * 100.0)


def ewma_vol_series(bars: pd.DataFrame, lam: float, smooth: int, estimator: str) -> pd.Series:
    """RiskMetrics-style EWMA volatility (annualized %), then an N-day simple smoothing.

    estimator: 'close' (close-to-close log returns), 'parkinson' (high/low range),
    'garman_klass' (OHLC).
    """
    o, h, l, c = bars["o"], bars["h"], bars["l"], bars["c"]
    if estimator == "close":
        x = np.log(c / c.shift(1)) ** 2
    elif estimator == "parkinson":
        x = np.log(h / l) ** 2 / (4.0 * math.log(2.0))
    elif estimator == "garman_klass":
        x = 0.5 * np.log(h / l) ** 2 - (2.0 * math.log(2.0) - 1.0) * np.log(c / o) ** 2
    else:
        raise ValueError(f"unknown vol_estimator {estimator!r}")
    x = x.dropna()
    var = x.ewm(alpha=1.0 - lam, adjust=False).mean()
    vol = np.sqrt(var * 252.0) * 100.0
    return vol.rolling(smooth).mean()


def average_correlation(returns: pd.DataFrame, days: int) -> pd.Series:
    """For each asset: mean pairwise correlation with the other assets over the last `days`."""
    window = returns.dropna().iloc[-days:]
    if len(window) < days:
        raise Halt(f"not enough aligned history for correlation ({len(window)} rows, need {days})")
    corr = window.corr()
    n = corr.shape[0]
    return (corr.sum() - 1.0) / (n - 1)


def wilder_atr(bars: pd.DataFrame, n: int) -> pd.Series:
    h, l, c = bars["h"], bars["l"], bars["c"]
    prev_c = c.shift(1)
    tr = pd.concat([h - l, (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False).mean()


def atr_trend_series(bars: pd.DataFrame, atr_days: int, up_days: int, low_days: int,
                     lower_variant: str, lag: int) -> pd.Series:
    """ATR Trend/Breakout state: +2 long, -2 neutral/short, 0 before the first signal.

    Upper band = highest close(up_days) + ATR(atr_days).
    Lower band = highest low(low_days) -/+ ATR(atr_days)  (paper is ambiguous; see config).
    A breakout on day t (vs. the previous day's bands) changes the state from day t+lag.
    """
    atr = wilder_atr(bars, atr_days)
    upper = bars["c"].rolling(up_days).max() + atr
    if lower_variant == "hhv_low_minus_atr":
        lower = bars["l"].rolling(low_days).max() - atr
    elif lower_variant == "hhv_low_plus_atr":
        lower = bars["l"].rolling(low_days).max() + atr
    else:
        raise ValueError(f"unknown lower_band {lower_variant!r}")
    up_prev, low_prev = upper.shift(1), lower.shift(1)
    state, out = 0, []
    for hi, lo, u, d in zip(bars["h"], bars["l"], up_prev, low_prev):
        if not np.isnan(u) and hi > u:
            state = 2
        elif not np.isnan(d) and lo < d:
            state = -2
        out.append(state)
    return pd.Series(out, index=bars.index).shift(lag).fillna(0).astype(int)


def rank_assets(M: pd.Series, V: pd.Series, C: pd.Series, T: pd.Series, cfg: dict,
                hurdle: float = 0.0):
    """Returns (table DataFrame sorted by score, target weights dict incl. cash).

    A selected asset keeps its slot only if its momentum beats `hurdle` (the cash asset's
    own momentum when ranking.momentum_hurdle == 'cash', else 0); otherwise the slot goes to cash.
    """
    amb, rk = cfg["ambiguities"], cfg["ranking"]
    if amb["rank_convention"] != "1_is_best":
        raise ValueError("only rank_convention '1_is_best' is implemented")
    order = list(M.index)
    df = pd.DataFrame({"M": M, "V": V, "C": C, "T": T}).loc[order]
    # tied values share an average rank so universe order never decides a factor
    df["rank_M"] = df["M"].rank(ascending=False, method="average")
    df["rank_V"] = df["V"].rank(ascending=True, method="average")
    df["rank_C"] = df["C"].rank(ascending=True, method="average")
    df["score"] = (rk["w_momentum"] * df["rank_M"] + rk["w_volatility"] * df["rank_V"]
                   + rk["w_correlation"] * df["rank_C"] - rk.get("w_trend", 1.0) * df["T"]
                   + amb["tiebreak_sign"] * df["M"] / rk["tiebreak_x"])
    df["_pos"] = range(len(df))
    df = df.sort_values(["score", "_pos"], kind="mergesort").drop(columns="_pos")
    top_n = rk["top_n"]
    df["selected"] = False
    df.iloc[:top_n, df.columns.get_loc("selected")] = True
    cash = cfg["universe"]["cash"]
    slot = 1.0 / top_n
    weights = {sym: 0.0 for sym in order}
    weights[cash] = 0.0
    df["weight"] = 0.0
    for sym in df.index[:top_n]:
        if df.at[sym, "M"] > hurdle:
            weights[sym] += slot
            df.at[sym, "weight"] = slot
        else:
            weights[cash] += slot
    weights = {k: round(v, 6) for k, v in weights.items()}
    return df, weights


def compute_signal(bars: dict[str, pd.DataFrame], cfg: dict, as_of: dt.date) -> dict:
    uni = cfg["universe"]
    risk, cash = uni["risk_assets"], uni["cash"]
    lb, amb = cfg["lookbacks"], cfg["ambiguities"]
    trimmed = {}
    for sym in tradable_symbols(cfg):
        b = bars.get(sym)
        if b is None or b.empty:
            raise Halt(f"no bars for {sym}")
        b = b[b.index <= as_of]
        if b.empty or b.index[-1] != as_of:
            last = None if b.empty else b.index[-1].isoformat()
            raise Halt(f"stale data for {sym}: last bar {last}, expected {as_of.isoformat()}")
        trimmed[sym] = b
    M, V, T = {}, {}, {}
    for sym in risk:
        b = trimmed[sym]
        M[sym] = momentum(b["c"], lb["momentum_days"])
        V[sym] = float(ewma_vol_series(b, lb["ewma_lambda"], lb["vol_smooth_days"],
                                       amb["vol_estimator"]).iloc[-1])
        T[sym] = int(atr_trend_series(b, lb["atr_days"], lb["upper_band_close_days"],
                                      lb["lower_band_low_days"], amb["lower_band"],
                                      amb["trend_signal_lag_days"]).iloc[-1])
    closes = pd.DataFrame({sym: trimmed[sym]["c"] for sym in risk})
    C = average_correlation(closes.pct_change(), lb["correlation_days"])
    for name, series in (("momentum", M), ("volatility", V)):
        bad = [s for s, v in series.items() if v is None or not np.isfinite(v)]
        if bad:
            raise Halt(f"non-finite {name} for {bad}")
    hurdle_mode = cfg["ranking"].get("momentum_hurdle", "zero")
    if hurdle_mode == "cash":
        hurdle = momentum(trimmed[cash]["c"], lb["momentum_days"])
    elif hurdle_mode == "zero":
        hurdle = 0.0
    else:
        raise ValueError(f"unknown momentum_hurdle {hurdle_mode!r}")
    if not np.isfinite(hurdle):
        raise Halt(f"non-finite momentum for cash asset {cash}")
    table, weights = rank_assets(pd.Series(M), pd.Series(V), C.loc[risk], pd.Series(T), cfg,
                                 hurdle=hurdle)
    rows = []
    for sym, r in table.iterrows():
        rows.append({
            "symbol": sym, "momentum_pct": round(float(r["M"]), 3),
            "vol_pct": round(float(r["V"]), 3), "avg_corr": round(float(r["C"]), 4),
            "trend": int(r["T"]), "rank_M": float(r["rank_M"]), "rank_V": float(r["rank_V"]),
            "rank_C": float(r["rank_C"]), "score": round(float(r["score"]), 4),
            "selected": bool(r["selected"]), "weight": round(float(r["weight"]), 4),
        })
    core, shield = portfolio_parts(cfg)
    return {
        "as_of": as_of.isoformat(),
        "month": month_key(as_of),
        "effective_month": next_month_key(as_of),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "params": {"lookbacks": lb, "ranking": cfg["ranking"], "ambiguities": amb},
        "portfolio": {"name": (cfg.get("portfolio") or {}).get("name", "RAAM"),
                      "core": core, "shield_weight": shield},
        "shield_targets": weights,
        "momentum_hurdle": {"mode": hurdle_mode, "value_pct": round(float(hurdle), 3),
                            "cash_asset": cash},
        "table": rows,
        "targets": combine_targets(weights, cfg),
        "executed": None,
    }


# --------------------------------------------------------------------------
# Order planning (pure - unit tested)
# --------------------------------------------------------------------------
def validate_targets(targets: dict, cfg: dict) -> None:
    uni = set(tradable_symbols(cfg))
    extra = [s for s, w in targets.items() if w > 0 and s not in uni]
    if extra:
        raise Halt(f"targets contain non-universe symbols {extra}")
    if any(w < 0 for w in targets.values()):
        raise Halt("negative target weight")
    total = sum(targets.values()) * 100.0
    tol = cfg["guardrails"]["weights_sum_tolerance_pct"]
    if abs(total - 100.0) > tol:
        raise Halt(f"target weights sum to {total:.3f}% (tolerance {tol}%)")


def plan_orders(targets: dict, equity: float, positions: dict, prices: dict, cfg: dict) -> dict:
    """positions: sym -> {'qty': float, 'market_value': float}; prices: sym -> last price."""
    validate_targets(targets, cfg)
    ex = cfg["execution"]
    uni = cfg["universe"]
    universe = set(tradable_symbols(cfg))
    investable = equity * (1.0 - ex["cash_buffer_pct"] / 100.0)
    sells, buys, warnings = [], [], []
    for sym in sorted(set(targets) | set(positions)):
        if sym not in universe:
            warnings.append(f"non-universe position {sym} left untouched")
            continue
        w = targets.get(sym, 0.0)
        pos = positions.get(sym, {"qty": 0.0, "market_value": 0.0})
        target_value = w * investable
        delta = target_value - pos["market_value"]
        if abs(delta) < ex["min_trade_usd"] and not (w == 0 and pos["qty"] > 0):
            continue
        if delta < 0:
            if w == 0:
                qty = pos["qty"]
            else:
                price = prices.get(sym)
                if not price:
                    raise Halt(f"no price for {sym}")
                qty = math.floor((-delta / price) * 1e6) / 1e6
            if qty > 0:
                sells.append({"symbol": sym, "side": "sell", "qty": round(qty, 6),
                              "est_value": round(-delta if w else pos["market_value"], 2),
                              "close_position": w == 0})
        else:
            buys.append({"symbol": sym, "side": "buy", "notional": round(delta, 2),
                         "est_value": round(delta, 2)})
    for o in buys:
        cap_key = ("max_order_pct_equity_cash" if o["symbol"] == uni["cash"]
                   else "max_order_pct_equity_risk_asset")
        pct = o["notional"] / equity * 100.0 if equity else float("inf")
        if pct > ex[cap_key]:
            raise Halt(f"order {o['symbol']} ${o['notional']} is {pct:.1f}% of equity "
                       f"(cap {ex[cap_key]}%)")
    return {"orders": sells + buys, "warnings": warnings,
            "equity": round(equity, 2), "investable": round(investable, 2)}


# --------------------------------------------------------------------------
# Alpaca REST client
# --------------------------------------------------------------------------
class Alpaca:
    def __init__(self):
        load_env()
        self.key = os.environ.get("ALPACA_API_KEY", "")
        self.secret = os.environ.get("ALPACA_SECRET_KEY", "")
        self.base = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets").rstrip("/")
        self.data = os.environ.get("ALPACA_DATA_URL", "https://data.alpaca.markets").rstrip("/")
        missing = [v for v in ("ALPACA_API_KEY", "ALPACA_SECRET_KEY") if not os.environ.get(v)]
        if missing:
            raise Halt(f"missing environment variable(s) {missing} - set them in the cloud "
                       "environment's Environment variables (or local .env for local testing)")
        paper = os.environ.get("PAPER_TRADING", "true").lower() != "false"
        if "paper-api" not in self.base:
            if paper or os.environ.get("LIVE_CONFIRM", "no").lower() != "yes":
                raise Halt(f"refusing non-paper endpoint {self.base} "
                           "(needs PAPER_TRADING=false and LIVE_CONFIRM=yes)")
        self.s = requests.Session()
        self.s.headers.update({"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret})

    def _req(self, method: str, url: str, **kw):
        for attempt in range(4):
            r = self.s.request(method, url, timeout=30, **kw)
            if r.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            if r.status_code >= 400:
                raise requests.HTTPError(f"{method} {url} -> {r.status_code}: {r.text[:300]}",
                                         response=r)
            return r.json() if r.text else None

    # trading API
    def account(self):
        return self._req("GET", f"{self.base}/v2/account")

    def positions(self):
        return self._req("GET", f"{self.base}/v2/positions")

    def clock(self):
        return self._req("GET", f"{self.base}/v2/clock")

    def calendar(self, start: dt.date, end: dt.date):
        return self._req("GET", f"{self.base}/v2/calendar",
                         params={"start": start.isoformat(), "end": end.isoformat()})

    def portfolio_history(self, start: dt.date, end: dt.date):
        return self._req("GET", f"{self.base}/v2/account/portfolio/history",
                         params={"start": start.isoformat(), "end": end.isoformat(),
                                 "timeframe": "1D"})

    def submit_order(self, **order):
        return self._req("POST", f"{self.base}/v2/orders", json=order)

    def get_order(self, order_id: str):
        return self._req("GET", f"{self.base}/v2/orders/{order_id}")

    # market data API
    def latest_prices(self, symbols: list[str]) -> dict:
        res = self._req("GET", f"{self.data}/v2/stocks/trades/latest",
                        params={"symbols": ",".join(symbols), "feed": "iex"})
        return {s: float(t["p"]) for s, t in (res.get("trades") or {}).items()}

    def bars(self, symbols: list[str], start: dt.date, end_utc: dt.datetime, feed: str,
             adjustment: str) -> dict[str, pd.DataFrame]:
        params = {"symbols": ",".join(symbols), "timeframe": "1Day", "start": start.isoformat(),
                  "end": end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"), "limit": 10000,
                  "adjustment": adjustment, "feed": feed}
        raw: dict[str, list] = {s: [] for s in symbols}
        while True:
            res = self._req("GET", f"{self.data}/v2/stocks/bars", params=params)
            for sym, rows in (res.get("bars") or {}).items():
                raw.setdefault(sym, []).extend(rows)
            token = res.get("next_page_token")
            if not token:
                break
            params["page_token"] = token
        out = {}
        for sym, rows in raw.items():
            if not rows:
                out[sym] = pd.DataFrame(columns=["o", "h", "l", "c", "v"])
                continue
            df = pd.DataFrame(rows)
            idx = pd.to_datetime(df["t"], utc=True).dt.tz_convert(ET).dt.date
            df = df.set_index(idx)[["o", "h", "l", "c", "v"]].astype(float)
            out[sym] = df[~df.index.duplicated(keep="last")].sort_index()
        return out


def fetch_bars(client: Alpaca, symbols: list[str], as_of: dt.date, cfg: dict):
    """Daily bars up to as_of. SIP first (free tier allows >15-min-old data), IEX fallback."""
    lb, data = cfg["lookbacks"], cfg["data"]
    start = as_of - dt.timedelta(days=lb["history_calendar_days"])
    end_of_day = dt.datetime.combine(as_of + dt.timedelta(days=1), dt.time(0), ET)
    latest_allowed = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=16)
    end_utc = min(end_of_day.astimezone(dt.timezone.utc), latest_allowed)
    try:
        return client.bars(symbols, start, end_utc, data["feed"], data["adjustment"]), data["feed"]
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code in (402, 403, 422):
            fb = data["fallback_feed"]
            return client.bars(symbols, start, end_utc, fb, data["adjustment"]), fb
        raise


def calendar_info(client: Alpaca, d: dt.date) -> dict:
    first = d.replace(day=1)
    last = (first + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)
    prev_first = (first - dt.timedelta(days=1)).replace(day=1)
    days = [dt.date.fromisoformat(x["date"]) for x in client.calendar(prev_first, last)]
    this_month = [x for x in days if x >= first]
    prev_month = [x for x in days if x < first]
    return {
        "date": d.isoformat(),
        "is_trading_day": d in this_month,
        "is_first_trading_day": bool(this_month) and d == this_month[0],
        "is_last_trading_day": bool(this_month) and d == this_month[-1],
        "first_trading_day": this_month[0].isoformat() if this_month else None,
        "last_trading_day": this_month[-1].isoformat() if this_month else None,
        "prev_month_last_trading_day": prev_month[-1].isoformat() if prev_month else None,
    }


# --------------------------------------------------------------------------
# Memory writers
# --------------------------------------------------------------------------
def signal_path(month: str) -> pathlib.Path:
    return SIGNALS_DIR / f"{month}.json"


def write_signal_log(sig: dict) -> None:
    header = f"## Signal {sig['month']} (as of {sig['as_of']}) -> allocation for {sig['effective_month']}"
    text = SIGNAL_LOG.read_text(encoding="utf-8") if SIGNAL_LOG.exists() else "# Signal Log\n"
    if header in text:
        return
    lines = ["", header, "",
             "| # | ETF | Mom % | Vol % | Avg corr | Trend | rM | rV | rC | Score | Weight |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(sig["table"], 1):
        mark = "**" if r["selected"] else ""
        lines.append(f"| {i} | {mark}{r['symbol']}{mark} | {r['momentum_pct']:.2f} | "
                     f"{r['vol_pct']:.2f} | {r['avg_corr']:.3f} | {r['trend']:+d} | {r['rank_M']:g} | "
                     f"{r['rank_V']:g} | {r['rank_C']:g} | {r['score']:.3f} | {r['weight'] * 100:.0f}% |")
    alloc = ", ".join(f"{s} {w * 100:.0f}%" for s, w in sig["targets"].items() if w > 0)
    h = sig.get("momentum_hurdle")
    hurdle = (f"**Momentum hurdle:** {h['value_pct']:.2f}% ({h['cash_asset']} 4-month momentum); "
              f"selected ETFs at or below it gave their slot to {h['cash_asset']}."
              if h and h["mode"] == "cash" else "**Momentum hurdle:** 0%")
    pf = sig.get("portfolio") or {}
    if pf.get("core"):
        shield = ", ".join(f"{s} {w * 100:.0f}%" for s, w in sig["shield_targets"].items() if w > 0)
        core = ", ".join(f"{s} {w * 100:.0f}%" for s, w in pf["core"].items())
        lines += ["", hurdle, "",
                  f"**Shield (RAAM, {pf['shield_weight'] * 100:.0f}% of portfolio):** {shield}",
                  f"**Core (fixed):** {core}", "",
                  f"**{pf.get('name', 'Portfolio')} target allocation:** {alloc}", ""]
    else:
        lines += ["", hurdle, "", f"**Target allocation:** {alloc}", ""]
    SIGNAL_LOG.write_text(text.rstrip("\n") + "\n" + "\n".join(lines), encoding="utf-8")


def append_trade_log(date: str, fills: list[dict], reason: str) -> None:
    text = TRADE_LOG.read_text(encoding="utf-8") if TRADE_LOG.exists() else ""
    rows = [f"| {date} | {f['symbol']} | {f['side']} | {f.get('filled_qty', '')} | "
            f"{f.get('filled_avg_price', '')} | {f.get('status', '')} | {reason} |" for f in fills]
    TRADE_LOG.write_text(text.rstrip("\n") + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------
def _wait(client: Alpaca, ids: list[str], seconds: int) -> dict:
    deadline, done = time.time() + seconds, {}
    while ids and time.time() < deadline:
        for oid in list(ids):
            o = client.get_order(oid)
            if o["status"] in ("filled", "canceled", "expired", "rejected", "done_for_day"):
                done[oid] = o
                ids.remove(oid)
        if ids:
            time.sleep(3)
    for oid in ids:
        done[oid] = client.get_order(oid)
    return done


def _fill_summary(o: dict) -> dict:
    return {"id": o["id"], "symbol": o["symbol"], "side": o["side"], "status": o["status"],
            "filled_qty": o.get("filled_qty"), "filled_avg_price": o.get("filled_avg_price"),
            "notional": o.get("notional"), "qty": o.get("qty")}


def execute_plan(client: Alpaca, plan: dict, cfg: dict) -> list[dict]:
    wait = cfg["execution"]["fill_wait_seconds"]
    sells = [o for o in plan["orders"] if o["side"] == "sell"]
    buys = [o for o in plan["orders"] if o["side"] == "buy"]
    results = []
    ids = []
    for o in sells:
        r = client.submit_order(symbol=o["symbol"], qty=str(o["qty"]), side="sell",
                                type="market", time_in_force="day")
        ids.append(r["id"])
    results += [_fill_summary(o) for o in _wait(client, ids, wait).values()]
    if buys:
        cash = float(client.account()["cash"])
        total = sum(o["notional"] for o in buys)
        scale = min(1.0, cash / total) if total > 0 else 1.0
        ids = []
        for o in buys:
            notional = math.floor(o["notional"] * scale * 100) / 100
            if notional < 1:
                continue
            r = client.submit_order(symbol=o["symbol"], notional=f"{notional:.2f}", side="buy",
                                    type="market", time_in_force="day")
            ids.append(r["id"])
        results += [_fill_summary(o) for o in _wait(client, ids, wait).values()]
    return results


def _positions_map(client: Alpaca) -> dict:
    return {p["symbol"]: {"qty": float(p["qty"]), "market_value": float(p["market_value"]),
                          "price": float(p["current_price"])} for p in client.positions()}


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def _resolve_date(arg: str | None) -> dt.date:
    return dt.date.fromisoformat(arg) if arg else today_et()


def cmd_calendar(args, cfg):
    return {"status": "ok", **calendar_info(Alpaca(), _resolve_date(args.date))}


def cmd_signal(args, cfg):
    client = Alpaca()
    d = _resolve_date(args.date)
    info = calendar_info(client, d)
    if not info["is_trading_day"]:
        return {"status": "noop", "reason": f"{d} is not a trading day"}
    if not info["is_last_trading_day"] and not args.force:
        return {"status": "noop", "reason": f"{d} is not the last trading day of the month "
                                            f"(that is {info['last_trading_day']})"}
    path = signal_path(month_key(d))
    if path.exists() and not args.dry_run:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing.get("executed"):
            return {"status": "noop", "reason": f"signal {path.name} already executed"}
    uni = cfg["universe"]
    bars, feed = fetch_bars(client, tradable_symbols(cfg), d, cfg)
    sig = compute_signal(bars, cfg, d)
    sig["data_feed"] = feed
    if not args.dry_run:
        SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sig, indent=2) + "\n", encoding="utf-8")
        write_signal_log(sig)
    return {"status": "ok", "dry_run": args.dry_run, "file": str(path.relative_to(ROOT)), **sig}


def _current_targets(state: dict, cfg: dict) -> tuple[dict | None, str]:
    cash = cfg["universe"]["cash"]
    if state["circuit_breaker"]["tripped"]:
        return {cash: 1.0}, "circuit_breaker"
    executed = sorted(p for p in SIGNALS_DIR.glob("*.json")
                      if json.loads(p.read_text(encoding="utf-8")).get("executed"))
    if not executed:
        return None, "none"
    sig = json.loads(executed[-1].read_text(encoding="utf-8"))
    return sig["targets"], f"signal {sig['month']}"


def cmd_rebalance(args, cfg):
    client = Alpaca()
    state = load_state()
    d = _resolve_date(args.date)
    info = calendar_info(client, d)
    breaker = state["circuit_breaker"]["tripped"]
    sig, path, reenter = None, None, False
    if breaker:
        targets, reason = {cfg["universe"]["cash"]: 1.0}, "circuit breaker: move to cash"
        # Auto re-entry: at the first monthly rebalance after the trip, follow the fresh signal.
        auto = cfg["guardrails"].get("circuit_breaker_reset", "manual") == "next_rebalance"
        if auto and info["is_trading_day"] and (info["is_first_trading_day"] or args.force):
            cand = signal_path(prev_month_key(d))
            tripped_on = state["circuit_breaker"].get("tripped_on") or "0000-00-00"
            if cand.exists():
                s = json.loads(cand.read_text(encoding="utf-8"))
                if not s.get("executed") and s["as_of"] >= tripped_on:
                    sig, path, reenter = s, cand, True
                    targets = s["targets"]
                    reason = f"circuit breaker auto re-entry ({s['month']} signal)"
    else:
        if not info["is_trading_day"]:
            return {"status": "noop", "reason": f"{d} is not a trading day"}
        if not info["is_first_trading_day"] and not args.force:
            return {"status": "noop", "reason": f"{d} is not the first trading day of the month"}
        path = signal_path(prev_month_key(d)) if not args.force else (
            sorted(SIGNALS_DIR.glob("*.json"))[-1] if list(SIGNALS_DIR.glob("*.json")) else None)
        if path is None or not path.exists():
            raise Halt(f"no signal file for {prev_month_key(d)} - month-end signal did not run")
        sig = json.loads(path.read_text(encoding="utf-8"))
        if sig.get("executed"):
            return {"status": "noop", "reason": f"signal {sig['month']} already executed"}
        targets, reason = sig["targets"], f"RAAM rebalance ({sig['month']} signal)"

    account = client.account()
    equity = float(account["equity"])
    positions = _positions_map(client)
    need = [s for s, w in targets.items() if w > 0 and s not in positions]
    prices = {s: p["price"] for s, p in positions.items()}
    if need:
        prices.update(client.latest_prices(need))
    plan = plan_orders(targets, equity, positions, prices, cfg)
    result = {"status": "ok", "reason": reason, "targets": targets, "plan": plan,
              "dry_run": args.dry_run, "breaker_reentry": reenter}
    if breaker and not reenter and not plan["orders"]:
        return {**result, "status": "noop", "reason": "circuit breaker tripped; already in cash"}
    if args.dry_run:
        return result
    if cfg["execution"]["require_approval"]:
        raise Halt("require_approval is on - orders not submitted (approval flow not built yet)")
    clock = client.clock()
    if not clock["is_open"]:
        raise Halt(f"market is closed (next open {clock['next_open']}); no orders submitted")
    fills = execute_plan(client, plan, cfg) if plan["orders"] else []
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    if sig is not None:
        sig["executed"] = {"at": now, "date": d.isoformat(), "fills": fills}
        path.write_text(json.dumps(sig, indent=2) + "\n", encoding="utf-8")
    if fills:
        append_trade_log(d.isoformat(), fills, reason)
    if reenter:
        # re-base the high-water mark so the old peak can't immediately re-trip the breaker
        state["circuit_breaker"] = {"tripped": False, "reason": None, "tripped_on": None,
                                    "last_reset": {"on": d.isoformat(), "mode": "auto",
                                                   "previous": state["circuit_breaker"]}}
        state["high_water_mark"] = round(equity, 2)
        save_state(state)
    bad = [f for f in fills if f["status"] != "filled"]
    result.update({"fills": fills, "unfilled": bad})
    if bad:
        result["status"] = "halt"
        result["reason"] = f"{len(bad)} order(s) not filled - check Alpaca"
    return result


def cmd_health(args, cfg):
    client = Alpaca()
    state = load_state()
    g = cfg["guardrails"]
    account = client.account()
    equity, last_equity = float(account["equity"]), float(account["last_equity"])
    positions = _positions_map(client)
    hwm = max(state["high_water_mark"] or equity, equity)
    drawdown = (equity / hwm - 1.0) * 100.0 if hwm else 0.0
    day_change = (equity / last_equity - 1.0) * 100.0 if last_equity else 0.0
    alerts = []
    if not state["circuit_breaker"]["tripped"]:
        why = None
        if drawdown <= -g["circuit_breaker_drawdown_pct"]:
            why = f"drawdown {drawdown:.2f}% from high-water mark {hwm:.2f}"
        elif day_change <= -g["circuit_breaker_daily_loss_pct"]:
            why = f"one-day loss {day_change:.2f}%"
        if why:
            state["circuit_breaker"] = {"tripped": True, "reason": why,
                                        "tripped_on": today_et().isoformat()}
            cash = cfg["universe"]["cash"]
            reentry = ("re-enters automatically at the next monthly rebalance"
                       if g.get("circuit_breaker_reset") == "next_rebalance"
                       else "stays in cash until manually reset in memory/state.json")
            alerts.append(f"CIRCUIT BREAKER TRIPPED: {why}. Next morning run moves to 100% {cash}; "
                          f"it {reentry}.")
    targets, target_src = _current_targets(state, cfg)
    universe = set(tradable_symbols(cfg))
    rows = []
    for sym in sorted(set(positions) | set(k for k, v in (targets or {}).items() if v > 0)):
        p = positions.get(sym, {"qty": 0.0, "market_value": 0.0})
        w = p["market_value"] / equity * 100.0 if equity else 0.0
        t = (targets or {}).get(sym, 0.0) * 100.0
        rows.append({"symbol": sym, "qty": p["qty"], "market_value": round(p["market_value"], 2),
                     "weight_pct": round(w, 2), "target_pct": round(t, 2),
                     "drift_pct": round(w - t, 2)})
        if sym not in universe:
            alerts.append(f"unexpected non-universe position {sym}")
    max_drift = max((abs(r["drift_pct"]) for r in rows), default=0.0) if targets else 0.0
    if targets and max_drift > 10:
        alerts.append(f"max drift {max_drift:.1f}% vs targets ({target_src})")
    snapshot = {"date": today_et().isoformat(), "equity": round(equity, 2)}
    if not args.dry_run:
        state["high_water_mark"] = round(hwm, 2)
        hist = [h for h in state["equity_history"] if h["date"] != snapshot["date"]]
        state["equity_history"] = (hist + [snapshot])[-500:]
        state["last_health"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        save_state(state)
    return {"status": "ok", "dry_run": args.dry_run, "equity": round(equity, 2),
            "cash": round(float(account["cash"]), 2), "day_change_pct": round(day_change, 3),
            "high_water_mark": round(hwm, 2), "drawdown_pct": round(drawdown, 3),
            "circuit_breaker": state["circuit_breaker"], "targets_source": target_src,
            "positions": rows, "alerts": alerts}


def _period_return(closes: pd.Series, start: dt.date, end: dt.date) -> float | None:
    s = closes[(closes.index >= start) & (closes.index <= end)]
    if len(s) < 2:
        return None
    return float((s.iloc[-1] / s.iloc[0] - 1.0) * 100.0)


def cmd_review(args, cfg):
    client = Alpaca()
    today = today_et()
    if args.month:
        month = args.month
    else:
        info = calendar_info(client, today)
        if not info["is_first_trading_day"] and not args.force:
            return {"status": "noop", "reason": f"{today} is not the first trading day of the month"}
        month = prev_month_key(today)
    y, m = map(int, month.split("-"))
    m_first = dt.date(y, m, 1)
    info_m = calendar_info(client, m_first)
    start = dt.date.fromisoformat(info_m["prev_month_last_trading_day"])
    end = dt.date.fromisoformat(info_m["last_trading_day"])
    hist = client.portfolio_history(start, end)
    eq = pd.Series(hist.get("equity") or [], index=[
        dt.datetime.fromtimestamp(t, ET).date() for t in (hist.get("timestamp") or [])],
        dtype=float).dropna()
    eq = eq[eq > 0]
    port_ret = _period_return(eq, start, end)
    uni = cfg["universe"]
    mixes = cfg.get("benchmark_mixes", {})
    # the 7Twelve benchmark keeps its original cash fund (SHY) even though RAAM now uses BIL
    ew_assets = uni["risk_assets"] + [SEVEN_TWELVE_CASH]
    mix_syms = [s for m in mixes.values() for s in m]
    syms = list(dict.fromkeys(tradable_symbols(cfg) + [SEVEN_TWELVE_CASH] + cfg["benchmarks"] + mix_syms))
    bars, _ = fetch_bars(client, syms, end, {**cfg, "lookbacks": {**cfg["lookbacks"],
                                                                  "history_calendar_days": 45}})
    etf_rets = {s: _period_return(bars[s]["c"], start, end) for s in tradable_symbols(cfg)}
    ew = [_period_return(bars[s]["c"], start, end) for s in ew_assets]
    valid = [v for v in ew if v is not None]
    bench = {s: _period_return(bars[s]["c"], start, end) for s in cfg["benchmarks"]}
    all_rets = {s: _period_return(bars[s]["c"], start, end) for s in syms}
    mix_rets = {}
    for name, w in mixes.items():
        vals = [all_rets.get(s) for s in w]
        mix_rets[name] = None if None in vals else sum(w[s] * all_rets[s] for s in w)
    sig_path = signal_path(prev_month_key(m_first))
    sig = json.loads(sig_path.read_text(encoding="utf-8")) if sig_path.exists() else None
    held = sig["targets"] if sig else None
    core, shield_w = portfolio_parts(cfg)

    def sleeve(weights):
        if not weights:
            return None
        vals = {s: all_rets.get(s) for s, w in weights.items() if w > 0}
        return None if None in vals.values() else sum(weights[s] * vals[s] for s in vals)
    shield_est = sleeve(sig.get("shield_targets", sig["targets"])) if sig else None
    core_est = sleeve({s: w / sum(core.values()) for s, w in core.items()}) if core else None

    def r(x):
        return None if x is None else round(x, 3)
    return {"status": "ok", "month": month, "period": [start.isoformat(), end.isoformat()],
            "portfolio": (cfg.get("portfolio") or {}).get("name", "RAAM"),
            "portfolio_return_pct": r(port_ret),
            "core_return_est_pct": r(core_est), "shield_return_est_pct": r(shield_est),
            "benchmark_mixes_pct": {k: r(v) for k, v in mix_rets.items()},
            "equity_start": r(float(eq.iloc[0])) if len(eq) else None,
            "equity_end": r(float(eq.iloc[-1])) if len(eq) else None,
            "benchmarks_pct": {k: r(v) for k, v in bench.items()},
            "equal_weight_7twelve_pct": r(sum(valid) / len(valid)) if valid else None,
            "etf_returns_pct": {k: r(v) for k, v in etf_rets.items()},
            "allocation_held": held}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("calendar", "signal", "rebalance"):
        sp = sub.add_parser(name)
        sp.add_argument("--date")
        if name != "calendar":
            sp.add_argument("--force", action="store_true")
            sp.add_argument("--dry-run", action="store_true")
    sp = sub.add_parser("health")
    sp.add_argument("--dry-run", action="store_true")
    sp = sub.add_parser("review")
    sp.add_argument("--month")
    sp.add_argument("--force", action="store_true")
    args = p.parse_args(argv)
    cfg = load_config()
    handlers = {"calendar": cmd_calendar, "signal": cmd_signal, "rebalance": cmd_rebalance,
                "health": cmd_health, "review": cmd_review}
    try:
        out = handlers[args.cmd](args, cfg)
        code = 2 if out.get("status") == "halt" else 0
    except Halt as e:
        out, code = {"status": "halt", "reason": str(e)}, 2
    except Exception as e:  # noqa: BLE001 - report everything as JSON for Claude
        out, code = {"status": "error", "reason": f"{type(e).__name__}: {e}"}, 1
    print(json.dumps(out, indent=2, default=str))
    return code


if __name__ == "__main__":
    sys.exit(main())
