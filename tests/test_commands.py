"""End-to-end tests of the raam.py commands against a fake Alpaca (no network)."""
import datetime as dt
import json
import pathlib
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import raam  # noqa: E402

CFG = raam.load_config()
CASH = CFG["universe"]["cash"]
SYMS = list(dict.fromkeys(raam.tradable_symbols(CFG) + ["SPY", "AGG"]))   # + benchmark ETFs
CORE_SYM = CFG["portfolio"]["core_trend"]["symbol"]
# Sept 2026: last trading day Wed 30th; Oct 2026: first trading day Thu 1st
SEPT_DAYS = [d.date() for d in pd.bdate_range("2026-09-01", "2026-09-30") if d.day != 7]  # Labor Day
OCT_DAYS = [d.date() for d in pd.bdate_range("2026-10-01", "2026-10-31")]


class FakeAlpaca:
    def __init__(self, equity=100_000.0, positions=None, is_open=True):
        self.equity = equity
        self._positions = positions or {}
        self.is_open = is_open
        self.submitted = []
        self.nonfrac = set()
        self.untradable = set()
        rng = np.random.default_rng(11)
        idx = pd.bdate_range(end="2026-09-30", periods=450).date
        self._bars = {}
        for i, s in enumerate(SYMS):
            drift = 0.001 if i % 2 == 0 else -0.0008
            if s == CORE_SYM:
                drift = 0.0015                  # Core trend filter ON by default in tests
            c = pd.Series(100 * np.cumprod(1 + rng.normal(drift, 0.01, len(idx))), index=idx)
            self._bars[s] = pd.DataFrame({"o": c, "h": c * 1.01, "l": c * 0.99, "c": c, "v": 1e6})

    def calendar(self, start, end):
        return [{"date": d.isoformat()} for d in SEPT_DAYS + OCT_DAYS if start <= d <= end]

    def bars(self, symbols, start, end_utc, feed, adjustment):
        return {s: self._bars[s] for s in symbols}

    def account(self):
        return {"equity": str(self.equity), "last_equity": str(self.equity), "cash": str(self.equity),
                "status": "ACTIVE", "trading_blocked": False, "account_blocked": False}

    def asset(self, sym):
        return {"symbol": sym, "tradable": sym not in self.untradable, "status": "active",
                "fractionable": sym not in self.nonfrac}

    def open_orders(self):
        return []

    def positions(self):
        return [{"symbol": s, "qty": str(p["qty"]), "market_value": str(p["market_value"]),
                 "current_price": str(p["market_value"] / p["qty"])} for s, p in self._positions.items()]

    def latest_prices(self, symbols):
        return {s: 100.0 for s in symbols}

    def clock(self):
        return {"is_open": self.is_open, "next_open": "2026-10-01T09:30:00-04:00"}

    def submit_order(self, **o):
        oid = f"id{len(self.submitted)}"
        self.submitted.append({**o, "id": oid})
        return {"id": oid}

    def get_order(self, oid):
        o = next(x for x in self.submitted if x["id"] == oid)
        return {"id": oid, "symbol": o["symbol"], "side": o["side"], "status": "filled",
                "filled_qty": o.get("qty", "1"), "filled_avg_price": "100.0",
                "notional": o.get("notional"), "qty": o.get("qty")}


@pytest.fixture
def env(tmp_path, monkeypatch):
    mem = tmp_path / "memory"
    (mem / "signals").mkdir(parents=True)
    monkeypatch.setattr(raam, "ROOT", tmp_path)
    monkeypatch.setattr(raam, "MEMORY", mem)
    monkeypatch.setattr(raam, "SIGNALS_DIR", mem / "signals")
    monkeypatch.setattr(raam, "STATE_PATH", mem / "state.json")
    monkeypatch.setattr(raam, "SIGNAL_LOG", mem / "SIGNAL-LOG.md")
    monkeypatch.setattr(raam, "TRADE_LOG", mem / "TRADE-LOG.md")
    fake = FakeAlpaca()
    monkeypatch.setattr(raam, "Alpaca", lambda: fake)
    monkeypatch.setattr(raam, "today_et", lambda: dt.date(2026, 9, 30))
    return SimpleNamespace(mem=mem, fake=fake, mp=monkeypatch)


def args(**kw):
    base = {"date": None, "force": False, "dry_run": False, "month": None}
    return SimpleNamespace(**{**base, **kw})


def test_signal_noop_mid_month(env):
    out = raam.cmd_signal(args(date="2026-09-15"), CFG)
    assert out["status"] == "noop"


def test_signal_month_end_writes_files(env):
    out = raam.cmd_signal(args(date="2026-09-30"), CFG)
    assert out["status"] == "ok"
    assert out["effective_month"] == "2026-10"
    saved = json.loads((env.mem / "signals" / "2026-09.json").read_text())
    assert saved["executed"] is None
    assert sum(saved["targets"].values()) == pytest.approx(1.0)
    assert "## Signal 2026-09" in (env.mem / "SIGNAL-LOG.md").read_text()


def test_signal_dry_run_writes_nothing(env):
    raam.cmd_signal(args(date="2026-09-30", dry_run=True), CFG)
    assert not (env.mem / "signals" / "2026-09.json").exists()


def test_rebalance_flow_and_idempotency(env):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    assert raam.cmd_rebalance(args(date="2026-10-02"), CFG)["status"] == "noop"  # not 1st day
    dry = raam.cmd_rebalance(args(date="2026-10-01", dry_run=True), CFG)
    assert dry["status"] == "ok" and not env.fake.submitted
    out = raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert out["status"] == "ok", out
    assert env.fake.submitted and all(o["side"] == "buy" for o in env.fake.submitted)
    assert json.loads((env.mem / "signals" / "2026-09.json").read_text())["executed"]
    assert "RAAM rebalance" in (env.mem / "TRADE-LOG.md").read_text()
    again = raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert again["status"] == "noop"


def test_rebalance_halts_without_signal(env):
    out_code = raam.main(["rebalance", "--date", "2026-10-01"])
    assert out_code == 2


def test_rebalance_halts_when_market_closed(env):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    env.fake.is_open = False
    with pytest.raises(raam.Halt, match="market is closed"):
        raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert not env.fake.submitted


def test_health_trips_breaker_then_rebalance_goes_to_cash(env):
    env.fake._positions = {"VV": {"qty": 400, "market_value": 40_000}}
    raam.cmd_health(args(), CFG)                       # HWM = 100k
    env.fake.equity = 79_000                           # -21% from peak (breaker at -20%)
    env.fake._positions = {"VV": {"qty": 400, "market_value": 20_000}}
    h = raam.cmd_health(args(), CFG)
    assert h["circuit_breaker"]["tripped"] and h["alerts"]
    out = raam.cmd_rebalance(args(date="2026-10-05"), CFG)   # any day
    syms = {(o["symbol"], o["side"]) for o in env.fake.submitted}
    assert ("VV", "sell") in syms and (CASH, "buy") in syms
    assert out["reason"].startswith("circuit breaker")


def _trip(env, on="2026-09-15"):
    state = raam.load_state()
    state["circuit_breaker"] = {"tripped": True, "reason": "test", "tripped_on": on}
    state["high_water_mark"] = 150_000.0
    raam.save_state(state)


def test_breaker_stays_in_cash_until_next_rebalance(env):
    _trip(env)
    out = raam.cmd_rebalance(args(date="2026-10-05"), CFG)       # not a rebalance day
    assert out["targets"] == {CASH: 1.0} and not out["breaker_reentry"]
    assert raam.load_state()["circuit_breaker"]["tripped"]


def test_breaker_auto_reentry_with_fresh_signal(env):
    _trip(env, on="2026-09-15")
    raam.cmd_signal(args(date="2026-09-30"), CFG)                 # signal after the trip
    out = raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert out["breaker_reentry"] and out["reason"].startswith("circuit breaker auto re-entry")
    assert out["targets"] == json.loads((env.mem / "signals" / "2026-09.json").read_text())["targets"]
    state = raam.load_state()
    assert not state["circuit_breaker"]["tripped"]
    assert state["circuit_breaker"]["last_reset"]["mode"] == "auto"
    assert state["high_water_mark"] == 100_000.0                  # re-based, not the old 150k peak


def test_breaker_dry_run_reentry_changes_nothing(env):
    _trip(env)
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    out = raam.cmd_rebalance(args(date="2026-10-01", dry_run=True), CFG)
    assert out["breaker_reentry"] and not env.fake.submitted
    assert raam.load_state()["circuit_breaker"]["tripped"]


def test_breaker_manual_mode_never_reenters(env):
    _trip(env)
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    cfg = json.loads(json.dumps(CFG))
    cfg["guardrails"]["circuit_breaker_reset"] = "manual"
    out = raam.cmd_rebalance(args(date="2026-10-01"), cfg)
    assert out["targets"] == {CASH: 1.0} and not out["breaker_reentry"]


def test_signal_records_cash_hurdle(env):
    out = raam.cmd_signal(args(date="2026-09-30", dry_run=True), CFG)
    h = out["momentum_hurdle"]
    assert h["mode"] == "cash" and h["cash_asset"] == CASH
    for row in out["table"]:
        if row["selected"] and row["weight"] > 0:
            assert row["momentum_pct"] > h["value_pct"]


def test_signal_combines_core_and_shield(env):
    out = raam.cmd_signal(args(date="2026-09-30", dry_run=True), CFG)
    t, sh = out["targets"], out["shield_targets"]
    _, shield = raam.portfolio_parts(CFG)
    core = out["portfolio"]["core"]                       # this month's Core, after the trend filter
    assert out["core_trend"]["on"] and core == {CORE_SYM: 0.5}
    assert sum(t.values()) == pytest.approx(1.0) and sum(sh.values()) == pytest.approx(1.0)
    for s in raam.tradable_symbols(CFG):
        assert t[s] == pytest.approx(core.get(s, 0.0) + shield * sh.get(s, 0.0))
    assert t[CORE_SYM] >= 0.50 - 1e-9


def test_first_rebalance_buys_core_within_caps(env):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    out = raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert out["status"] == "ok", out
    bought = {o["symbol"] for o in env.fake.submitted}
    assert CORE_SYM in bought                              # a 50% buy fits the 55% order cap


# ---------------------------------------------------------------- preflight / execution quality
def test_preflight_ok(env):
    out = raam.cmd_preflight(args(), CFG)
    assert out["status"] == "ok", out
    assert set(out["assets"]) == set(raam.tradable_symbols(CFG))
    assert out["next_rebalance_day"] == "2026-10-01"
    assert out["next_signal_day"] == "2026-09-30"


def test_preflight_warns_non_fractionable_and_halts_untradable(env):
    env.fake.nonfrac = {"IGOV"}
    out = raam.cmd_preflight(args(), CFG)
    assert out["status"] == "ok" and any("IGOV" in w for w in out["warnings"])
    env.fake.untradable = {"RWR"}
    out = raam.cmd_preflight(args(), CFG)
    assert out["status"] == "halt" and "RWR" in out["reason"]


def test_rebalance_uses_whole_shares_for_non_fractionable(env):
    env.fake.nonfrac = {CORE_SYM}
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    out = raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert out["status"] == "ok", out
    core = [o for o in env.fake.submitted if o["symbol"] == CORE_SYM]
    assert core and "notional" not in core[0] and float(core[0]["qty"]).is_integer()
    others = [o for o in env.fake.submitted if o["symbol"] != CORE_SYM]
    assert all("notional" in o for o in others)
    assert out["plan"]["whole_share_symbols"] == [CORE_SYM]


def test_rebalance_halts_on_untradable_asset(env):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    env.fake.untradable = {CORE_SYM}
    with pytest.raises(raam.Halt, match="not tradable"):
        raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert not env.fake.submitted


def test_slippage_recorded_in_fills_and_trade_log(env):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    out = raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert all(f["ref_price"] == 100.0 and f["slippage_bps"] == 0.0 for f in out["fills"])
    assert out["slippage"]["avg_bps"] == 0.0
    row = [ln for ln in (env.mem / "TRADE-LOG.md").read_text().splitlines() if f"| {CORE_SYM} |" in ln][0]
    assert row.count("|") == 10          # date, sym, side, qty, fill, ref, slippage, status, reason


def test_slippage_sign_convention():
    assert raam.slippage_bps("buy", 100, 100.1) == 10.0     # paid up = cost
    assert raam.slippage_bps("sell", 100, 99.9) == 10.0     # sold lower = cost
    assert raam.slippage_bps("buy", 100, 99.95) == -5.0     # price improvement
    assert raam.slippage_bps("buy", None, 100) is None


def test_core_trend_filter_moves_core_to_cash_when_below_average(env):
    b = env.fake._bars[CORE_SYM]
    b[["o", "h", "l", "c"]] = b[["o", "h", "l", "c"]].mul(np.linspace(1.6, 1.0, len(b)), axis=0)
    out = raam.cmd_signal(args(date="2026-09-30", dry_run=True), CFG)
    ct = out["core_trend"]
    assert ct["on"] is False and ct["month_end_close"] < ct["sma"] and ct["off_to"] == CASH
    assert out["targets"].get(CORE_SYM, 0) == 0
    assert out["targets"][CASH] >= 0.5 - 1e-9
    assert sum(out["targets"].values()) == pytest.approx(1.0)


def test_core_trend_filter_needs_enough_history(env):
    env.fake._bars[CORE_SYM] = env.fake._bars[CORE_SYM].iloc[-150:]     # ~7 month-ends < 10
    assert raam.main(["signal", "--date", "2026-09-30"]) == 2


def test_rebalance_sells_previous_core_holding(env):
    """SPY (the previous Core) is sell-only: the switch to the QQQM Core sells it all and never buys it."""
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    env.fake._positions = {"SPY": {"qty": 300.0, "market_value": 30_000.0}}
    out = raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    assert out["status"] == "ok", out
    spy = [o for o in env.fake.submitted if o["symbol"] == "SPY"]
    assert len(spy) == 1 and spy[0]["side"] == "sell" and float(spy[0]["qty"]) == 300.0
    assert not any("SPY" in w for w in out["plan"]["warnings"])


def test_preflight_does_not_warn_about_sell_only_holdings(env):
    env.fake._positions = {"SPY": {"qty": 300.0, "market_value": 30_000.0}}
    out = raam.cmd_preflight(args(), CFG)
    assert out["status"] == "ok" and not any("SPY" in w for w in out["warnings"])
