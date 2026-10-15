import datetime as dt
import json
import os
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import raam  # noqa: E402

CFG = raam.load_config()
RISK = CFG["universe"]["risk_assets"]
R11 = ["VV", "IJH", "IJR", "EFA", "EEM", "RWR", "DBC", "VAW", "AGG", "TIP", "IGOV"]  # fixed set for pure ranking tests
CASH = CFG["universe"]["cash"]


def make_bars(closes, start=dt.date(2024, 1, 1), spread=0.01):
    idx = pd.bdate_range(start, periods=len(closes)).date
    c = pd.Series(closes, index=idx, dtype=float)
    return pd.DataFrame({"o": c.shift(1).fillna(c.iloc[0]), "h": c * (1 + spread),
                         "l": c * (1 - spread), "c": c, "v": 1e6})


# ---------------------------------------------------------------- indicators
def test_momentum_roc_percent():
    s = pd.Series(np.linspace(100, 200, 101))
    assert raam.momentum(s, 100) == pytest.approx(100.0)
    assert raam.momentum(s, 50) == pytest.approx((200 / 150 - 1) * 100)


def test_momentum_insufficient_history():
    with pytest.raises(raam.Halt):
        raam.momentum(pd.Series([1.0, 2.0]), 5)


def test_ewma_vol_constant_returns_is_zero_and_noisier_is_higher():
    flat = make_bars(np.full(300, 100.0))
    calm = make_bars(100 * np.cumprod(1 + np.random.default_rng(1).normal(0, 0.002, 300)))
    wild = make_bars(100 * np.cumprod(1 + np.random.default_rng(1).normal(0, 0.02, 300)))
    v_flat = raam.ewma_vol_series(flat, 0.94, 10, "close").iloc[-1]
    v_calm = raam.ewma_vol_series(calm, 0.94, 10, "close").iloc[-1]
    v_wild = raam.ewma_vol_series(wild, 0.94, 10, "close").iloc[-1]
    assert v_flat == pytest.approx(0.0)
    assert v_wild > v_calm * 5
    # ~2% daily -> ~32% annualized
    assert 15 < v_wild < 50


@pytest.mark.parametrize("est", ["close", "parkinson", "garman_klass"])
def test_vol_estimators_run(est):
    b = make_bars(100 * np.cumprod(1 + np.random.default_rng(2).normal(0, 0.01, 200)))
    assert np.isfinite(raam.ewma_vol_series(b, 0.94, 10, est).iloc[-1])


def test_average_correlation():
    rng = np.random.default_rng(3)
    base = rng.normal(0, 1, 200)
    df = pd.DataFrame({"A": base, "B": base + rng.normal(0, 0.01, 200),
                       "C": rng.normal(0, 1, 200)})
    ac = raam.average_correlation(df, 84)
    assert ac["A"] > 0.4 and ac["B"] > 0.4
    assert abs(ac["C"]) < 0.2


def test_atr_trend_breakout_then_crash():
    # flat base, a +15% breakout that holds, then a slide
    closes = np.concatenate([np.full(150, 100.0), np.full(60, 115.0), np.linspace(115, 80, 60)])
    b = make_bars(closes)
    t = raam.atr_trend_series(b, 42, 63, 105, "hhv_low_minus_atr", 1)
    assert t.iloc[0] == 0
    assert t.iloc[150] == 0          # signal takes effect the session after the breakout
    assert t.iloc[151] == 2
    assert t.iloc[-1] == -2


# ---------------------------------------------------------------- ranking
def _factors(mom):
    M = pd.Series(mom, index=R11, dtype=float)
    V = pd.Series(10.0, index=R11)
    C = pd.Series(0.5, index=R11)
    T = pd.Series(0, index=R11)
    return M, V, C, T


def test_rank_selects_top5_by_momentum_when_other_factors_equal():
    M, V, C, T = _factors(range(1, 12))  # IGOV highest momentum
    table, w = raam.rank_assets(M, V, C, T, CFG)
    assert list(table.index[:5]) == R11[::-1][:5]
    assert sum(w.values()) == pytest.approx(1.0)
    assert w[CASH] == 0.0
    assert all(w[s] == pytest.approx(0.2) for s in R11[::-1][:5])


def test_negative_momentum_goes_to_cash():
    M, V, C, T = _factors([-5, -4, -3, -2, -1, 1, 2, 3, -6, -7, -8])
    _, w = raam.rank_assets(M, V, C, T, CFG)
    assert w[CASH] == pytest.approx(0.4)
    assert sum(w.values()) == pytest.approx(1.0)


def test_all_negative_is_100pct_cash():
    M, V, C, T = _factors([-1.0] * 11)
    _, w = raam.rank_assets(M, V, C, T, CFG)
    assert w[CASH] == pytest.approx(1.0)


def test_trend_long_improves_rank_when_weighted():
    cfg = json.loads(json.dumps(CFG))
    cfg["ranking"]["w_trend"] = 1
    M, V, C, T = _factors([5.0] * 11)
    T["VV"] = 2
    table, _ = raam.rank_assets(M, V, C, T, cfg)
    assert table.index[0] == "VV"


def test_trend_ignored_when_weight_zero():
    cfg = json.loads(json.dumps(CFG))
    cfg["ranking"]["w_trend"] = 0
    M, V, C, T = _factors(range(1, 12))
    base, _ = raam.rank_assets(M, V, C, T, cfg)
    T["VV"] = 2          # VV has the lowest momentum; trend must not lift it
    T["IGOV"] = -2
    withT, _ = raam.rank_assets(M, V, C, T, cfg)
    assert list(base.index) == list(withT.index)


def test_low_vol_and_low_corr_rank_best():
    M, V, C, T = _factors([5.0] * 11)
    V["AGG"], C["AGG"] = 1.0, -0.5
    table, _ = raam.rank_assets(M, V, C, T, CFG)
    assert table.index[0] == "AGG"


def test_compute_signal_end_to_end_and_stale_guard():
    rng = np.random.default_rng(7)
    bars = {s: make_bars(100 * np.cumprod(1 + rng.normal(0.0005, 0.01, 400)))
            for s in raam.tradable_symbols(CFG)}
    as_of = bars["VV"].index[-1]
    sig = raam.compute_signal(bars, CFG, as_of)
    assert len(sig["table"]) == len(RISK) == 12
    assert sum(sig["targets"].values()) == pytest.approx(1.0)
    assert sum(r["selected"] for r in sig["table"]) == 5
    bars["EEM"] = bars["EEM"].iloc[:-1]
    with pytest.raises(raam.Halt, match="stale"):
        raam.compute_signal(bars, CFG, as_of)


# ---------------------------------------------------------------- order planning
def test_plan_from_cash_buys_five_slots():
    targets = {s: 0.0 for s in RISK} | {CASH: 0.0}
    for s in RISK[:5]:
        targets[s] = 0.2
    plan = raam.plan_orders(targets, 100_000, {}, {}, CFG)
    assert [o["side"] for o in plan["orders"]] == ["buy"] * 5
    assert sum(o["notional"] for o in plan["orders"]) == pytest.approx(99_500, abs=1)


def test_plan_sells_before_buys_and_closes_dropped():
    targets = {"VV": 0.2, "IJH": 0.2, "EFA": 0.2, "DBC": 0.2, CASH: 0.2}
    positions = {"VV": {"qty": 100, "market_value": 20_000},
                 "EEM": {"qty": 50, "market_value": 20_000}}
    plan = raam.plan_orders(targets, 100_000, positions, {"VV": 200.0}, CFG)
    sides = [o["side"] for o in plan["orders"]]
    assert sides.index("buy") > sides.index("sell")
    eem = next(o for o in plan["orders"] if o["symbol"] == "EEM")
    assert eem["side"] == "sell" and eem["qty"] == 50 and eem["close_position"]


def test_plan_rejects_bad_weights_and_foreign_symbols():
    with pytest.raises(raam.Halt, match="sum"):
        raam.plan_orders({"VV": 0.5}, 100_000, {}, {}, CFG)
    with pytest.raises(raam.Halt, match="non-universe"):
        raam.plan_orders({"TSLA": 1.0}, 100_000, {}, {}, CFG)


def test_plan_leaves_non_universe_positions_alone():
    plan = raam.plan_orders({CASH: 1.0}, 100_000, {"AAPL": {"qty": 1, "market_value": 200}},
                            {}, CFG)
    assert all(o["symbol"] != "AAPL" for o in plan["orders"])
    assert any("AAPL" in w for w in plan["warnings"])


def test_plan_allows_100pct_cash_but_caps_risk_asset():
    plan = raam.plan_orders({CASH: 1.0}, 100_000, {}, {}, CFG)
    assert plan["orders"][0]["symbol"] == CASH
    with pytest.raises(raam.Halt, match="cap"):
        raam.plan_orders({"VV": 1.0}, 100_000, {}, {}, CFG)


def test_month_helpers():
    assert raam.prev_month_key(dt.date(2026, 1, 2)) == "2025-12"
    assert raam.next_month_key(dt.date(2026, 12, 31)) == "2027-01"


# ---------------------------------------------------------------- env handling
def test_env_vars_win_and_dotenv_ignored_in_cloud(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("ALPACA_API_KEY=from_file\nDISCORD_WEBHOOK_URL=file_only\n")
    monkeypatch.setattr(raam, "ROOT", tmp_path)
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    monkeypatch.setenv("ALPACA_API_KEY", "from_env")

    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    raam.load_env()
    assert "DISCORD_WEBHOOK_URL" not in os.environ   # cloud: .env never read

    monkeypatch.delenv("CLAUDE_CODE_REMOTE")
    raam.load_env()
    env = os.environ
    assert env["ALPACA_API_KEY"] == "from_env"                      # real env var wins
    assert env["DISCORD_WEBHOOK_URL"] == "file_only"                 # local .env fills gaps


def test_cash_hurdle_sends_weak_momentum_to_cash():
    M, V, C, T = _factors(range(1, 12))              # top-5 momenta are 11, 10, 9, 8, 7
    _, w = raam.rank_assets(M, V, C, T, CFG, hurdle=8.5)
    assert w["IGOV"] == pytest.approx(0.2) and w["TIP"] == pytest.approx(0.2) and w["AGG"] == pytest.approx(0.2)
    assert w["VAW"] == 0.0 and w["DBC"] == 0.0       # 8 and 7 do not beat the 8.5% hurdle
    assert w[CASH] == pytest.approx(0.4)


def test_compute_signal_uses_cash_momentum_as_hurdle():
    rng = np.random.default_rng(9)
    bars = {s: make_bars(100 * np.cumprod(1 + rng.normal(0.0005, 0.01, 400)))
            for s in raam.tradable_symbols(CFG)}
    bars[CASH] = make_bars(100 * np.cumprod(np.full(400, 1.004)), spread=0.0001)  # ~40% in 84d
    sig = raam.compute_signal(bars, CFG, bars["VV"].index[-1])
    assert sig["momentum_hurdle"]["value_pct"] > 30
    assert sig["shield_targets"][CASH] == pytest.approx(1.0)  # nothing beats a 40% hurdle
    _, shield = raam.portfolio_parts(CFG)
    assert sig["targets"][CASH] == pytest.approx(shield)   # Core stays invested



# ---------------------------------------------------------------- Core & Shield
def test_combine_targets_core_plus_half_shield():
    cfg = json.loads(json.dumps(CFG))
    cfg["portfolio"] = {"core": {"SPY": 0.3, "AGG": 0.2}, "shield_weight": 0.5}
    t = raam.combine_targets({"VV": 0.2, "AGG": 0.2, "EFA": 0.2, CASH: 0.4}, cfg)
    assert t["SPY"] == pytest.approx(0.30) and t["AGG"] == pytest.approx(0.30)
    assert t["VV"] == pytest.approx(0.10) and t[CASH] == pytest.approx(0.20)
    assert sum(t.values()) == pytest.approx(1.0)


def test_raam_alone_when_no_portfolio_section():
    cfg = json.loads(json.dumps(CFG))
    cfg.pop("portfolio")
    assert raam.portfolio_parts(cfg) == ({}, 1.0)
    shield = {"VV": 0.2, "EFA": 0.2, "RWR": 0.2, CASH: 0.4}
    t = raam.combine_targets(shield, cfg)
    assert {k: v for k, v in t.items() if v} == shield


def test_bad_portfolio_split_rejected():
    cfg = json.loads(json.dumps(CFG))
    cfg["portfolio"] = {"core": {"SPY": 0.3}, "shield_weight": 0.5}
    with pytest.raises(ValueError):
        raam.portfolio_parts(cfg)


def test_plan_accepts_core_targets():
    t = raam.combine_targets({"VV": 0.2, "AGG": 0.2, "EFA": 0.2, CASH: 0.4}, CFG)
    plan = raam.plan_orders(t, 100_000, {}, {}, CFG)
    assert {o["symbol"] for o in plan["orders"]} >= set(CFG["portfolio"]["core"]) | {"AGG"}



# ---------------------------------------------------------------- IBIT cap
def test_ibit_is_in_universe_and_capped_in_config():
    assert "IBIT" in RISK and CFG["portfolio"]["max_weight"]["IBIT"] == 0.05


def test_cap_moves_excess_to_cash():
    t = raam.combine_targets({"IBIT": 0.2, "VV": 0.2, "EFA": 0.2, "AGG": 0.2, CASH: 0.2}, CFG)
    assert t["IBIT"] == pytest.approx(0.10)                  # 0.5 x 20% before the cap
    capped, applied = raam.apply_caps(t, CFG)
    assert capped["IBIT"] == pytest.approx(0.05)
    assert capped[CASH] == pytest.approx(t[CASH] + 0.05)
    assert sum(capped.values()) == pytest.approx(1.0)
    assert applied["IBIT"]["to_cash"] == pytest.approx(0.05)


def test_no_cap_when_ibit_not_selected():
    t = raam.combine_targets({"VV": 0.2, "EFA": 0.2, "AGG": 0.2, "TIP": 0.2, CASH: 0.2}, CFG)
    capped, applied = raam.apply_caps(t, CFG)
    assert capped == t and applied == {}


def test_signal_respects_ibit_cap_end_to_end():
    rng = np.random.default_rng(21)
    bars = {s: make_bars(100 * np.cumprod(1 + rng.normal(0.0002, 0.005, 400)))
            for s in raam.tradable_symbols(CFG)}
    bars["IBIT"] = make_bars(100 * np.cumprod(1 + rng.normal(0.004, 0.01, 400)))   # strong momentum
    sig = raam.compute_signal(bars, CFG, bars["VV"].index[-1])
    assert sig["targets"]["IBIT"] <= 0.05 + 1e-9
    assert sum(sig["targets"].values()) == pytest.approx(1.0)
    if sig["shield_targets"].get("IBIT", 0) > 0:
        assert "IBIT" in sig["caps_applied"]
