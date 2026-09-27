"""Fault drills: bad data and broker failures must end in a safe halt, never a wrong trade."""
import copy
import json

import numpy as np
import pytest
import requests

from test_commands import CASH, CFG, SYMS, args, env  # noqa: F401 - env is a fixture

import raam

FAST = copy.deepcopy(CFG)
FAST["execution"]["fill_wait_seconds"] = 0          # don't sit in the fill-polling loop


def _signal(env):
    out = raam.cmd_signal(args(date="2026-09-30"), CFG)
    assert out["status"] == "ok", out
    return out["targets"]


def _hold_unwanted(env, targets, value=100_000.0):
    """Start fully invested in a universe ETF the new signal doesn't want, so the rebalance sells then buys."""
    sym = next(s for s in SYMS if targets.get(s, 0) == 0)
    env.fake._positions = {sym: {"qty": 1000.0, "market_value": value}}
    return sym


def _statuses(env, by_symbol):
    orig = env.fake.get_order

    def get_order(oid):
        o = orig(oid)
        if o["symbol"] in by_symbol:
            o["status"] = by_symbol[o["symbol"]]
            if o["status"] != "filled":
                o["filled_qty"], o["filled_avg_price"] = "0", None
        return o
    env.mp.setattr(env.fake, "get_order", get_order)


def _signal_code(env):
    return raam.main(["signal", "--date", "2026-09-30"])


# ---------------------------------------------------------------- broker failures
def test_rejected_buy_halts_and_is_recorded(env):
    targets = _signal(env)
    _hold_unwanted(env, targets)
    _statuses(env, {"SPY": "rejected"})
    out = raam.cmd_rebalance(args(date="2026-10-01"), FAST)
    assert out["status"] == "halt"
    assert [f["symbol"] for f in out["unfilled"]] == ["SPY"]
    sig = json.loads((env.mem / "signals" / "2026-09.json").read_text())
    assert sig["executed"]                              # recorded, so it is never re-run blindly
    assert "rejected" in (env.mem / "TRADE-LOG.md").read_text()


def test_partial_fill_halts(env):
    targets = _signal(env)
    _hold_unwanted(env, targets)
    _statuses(env, {"AGG": "partially_filled"})
    out = raam.cmd_rebalance(args(date="2026-10-01"), FAST)
    assert out["status"] == "halt"
    assert "AGG" in [f["symbol"] for f in out["unfilled"]]


def test_api_error_mid_rebalance_stops_submitting(env):
    targets = _signal(env)
    _hold_unwanted(env, targets)
    orig = env.fake.submit_order

    def submit(**o):
        if o["side"] == "buy":
            raise requests.HTTPError("POST /v2/orders -> 503: service unavailable")
        return orig(**o)
    env.mp.setattr(env.fake, "submit_order", submit)
    assert raam.main(["rebalance", "--date", "2026-10-01"]) == 1        # error, not retried
    assert all(o["side"] == "sell" for o in env.fake.submitted)          # nothing after the failure
    sig = json.loads((env.mem / "signals" / "2026-09.json").read_text())
    assert not sig["executed"]


@pytest.mark.xfail(strict=True, reason="finding F1: sells that filled before a mid-rebalance API "
                                       "error are not written to TRADE-LOG or the signal file")
def test_api_error_mid_rebalance_logs_completed_sells(env):
    targets = _signal(env)
    sold = _hold_unwanted(env, targets)
    orig = env.fake.submit_order

    def submit(**o):
        if o["side"] == "buy":
            raise requests.HTTPError("POST /v2/orders -> 503: service unavailable")
        return orig(**o)
    env.mp.setattr(env.fake, "submit_order", submit)
    raam.main(["rebalance", "--date", "2026-10-01"])
    log = env.mem / "TRADE-LOG.md"
    assert log.exists() and sold in log.read_text()


def test_buys_are_scaled_to_available_cash(env):
    """A position outside the universe ties up cash: buys shrink to fit, nothing is bought on margin."""
    _signal(env)
    env.fake._positions = {"TSLA": {"qty": 300.0, "market_value": 60_000.0}}
    env.mp.setattr(env.fake, "account", lambda: {
        "equity": "100000", "last_equity": "100000", "cash": "40000",
        "status": "ACTIVE", "trading_blocked": False, "account_blocked": False})
    out = raam.cmd_rebalance(args(date="2026-10-01"), FAST)
    assert out["status"] == "ok", out
    assert any("TSLA" in w for w in out["plan"]["warnings"])
    assert not any(o["symbol"] == "TSLA" for o in env.fake.submitted)
    assert sum(float(o["notional"]) for o in env.fake.submitted if o["side"] == "buy") <= 40_000


# ---------------------------------------------------------------- bad market data
@pytest.mark.xfail(strict=True, reason="finding F2: a present-but-blank (NaN) latest close is dropped, so "
                                       "that ETF is silently ranked on the previous day's price")
def test_nan_latest_close_halts(env):
    env.fake._bars["EEM"].iloc[-1, env.fake._bars["EEM"].columns.get_loc("c")] = np.nan
    assert _signal_code(env) == 2
    assert not (env.mem / "signals" / "2026-09.json").exists()


def test_missing_symbol_halts(env):
    full = env.fake.bars
    env.mp.setattr(env.fake, "bars", lambda symbols, *a, **k:
                   {s: b for s, b in full(symbols, *a, **k).items() if s != "IBIT"})
    assert _signal_code(env) == 2
    assert not (env.mem / "signals" / "2026-09.json").exists()


def test_stale_data_halts(env):
    env.fake._bars["DBC"] = env.fake._bars["DBC"].iloc[:-1]
    assert _signal_code(env) == 2


def test_zero_price_in_lookback_halts(env):
    b = env.fake._bars["IJR"]
    b.iloc[-(CFG["lookbacks"]["momentum_days"] + 1), b.columns.get_loc("c")] = 0.0
    assert _signal_code(env) == 2
    assert not (env.mem / "signals" / "2026-09.json").exists()


# ---------------------------------------------------------------- extreme but valid markets
def test_bitcoin_melt_up_still_capped(env):
    b = env.fake._bars["IBIT"]
    b[["o", "h", "l", "c"]] = b[["o", "h", "l", "c"]].mul(np.linspace(1, 6, len(b)), axis=0)
    targets = _signal(env)
    assert targets.get("IBIT", 0) <= CFG["portfolio"]["max_weight"]["IBIT"] + 1e-9
    assert sum(targets.values()) == pytest.approx(1.0)


def test_everything_falling_sends_shield_to_cash(env):
    for s in CFG["universe"]["risk_assets"]:
        b = env.fake._bars[s]
        b[["o", "h", "l", "c"]] = b[["o", "h", "l", "c"]].mul(np.linspace(1, 0.2, len(b)), axis=0)
    targets = _signal(env)
    core = CFG["portfolio"]["core"]
    assert targets[CASH] == pytest.approx(CFG["portfolio"]["shield_weight"])
    assert {s: w for s, w in targets.items() if s != CASH and w > 0} == pytest.approx(core)
