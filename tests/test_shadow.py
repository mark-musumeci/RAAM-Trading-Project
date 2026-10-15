"""Tests for scripts/shadow.py (shadow variants) against a fake Alpaca (no network)."""
import datetime as dt
import json
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import raam  # noqa: E402
import shadow  # noqa: E402
from test_commands import CFG, OCT_DAYS, SEPT_DAYS, args, env  # noqa: E402,F401  (env is a fixture)
from test_report import FakeWithHistory  # noqa: E402

NOV_DAYS = [d.date() for d in pd.bdate_range("2026-11-02", "2026-11-30") if d.day != 26]  # Thanksgiving
SCFG = shadow.load_shadow_config()


class ShadowFake(FakeWithHistory):
    """Extends the fake's prices from October to mid-November so months can complete."""

    def __init__(self):
        super().__init__()
        rng = np.random.default_rng(3)
        g = self._bars["TIP"].copy()                     # a stand-in price series for GLD
        self._bars["GLD"] = g * 1.7
        extra = [d for d in OCT_DAYS + NOV_DAYS if d <= dt.date(2026, 11, 6)]
        for s, b in self._bars.items():
            c = float(b["c"].iloc[-1]) * np.cumprod(1 + rng.normal(0.0005, 0.01, len(extra)))
            o = np.concatenate([[float(b["c"].iloc[-1])], c[:-1]])
            ext = pd.DataFrame({"o": o, "h": np.maximum(o, c) * 1.002, "l": np.minimum(o, c) * 0.998,
                                "c": c, "v": 1e6}, index=extra)
            self._bars[s] = pd.concat([b, ext])

    def calendar(self, start, end):
        return [{"date": d.isoformat()} for d in SEPT_DAYS + OCT_DAYS + NOV_DAYS if start <= d <= end]


@pytest.fixture
def senv(env):
    fake = ShadowFake()
    env.mp.setattr(raam, "Alpaca", lambda: fake)
    env.fake = fake
    return env


def sargs(**kw):
    base = {"date": None, "force": False, "dry_run": False}
    return type("A", (), {**base, **kw})()


def test_noop_without_a_signal(senv):
    assert shadow.run(sargs(date="2026-10-14"))["status"] == "noop"


def test_records_variants_and_writes_log(senv):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    out = shadow.run(sargs(date="2026-10-14"))
    assert out["status"] == "ok" and out["recorded"] == ["2026-09"]
    rec = json.loads((senv.mem / "shadow" / "2026-09.json").read_text())
    live = json.loads((senv.mem / "signals" / "2026-09.json").read_text())
    v = rec["variants"]
    assert set(v) == set(SCFG["variants"])
    assert v["Live model"]["targets"] == {s: w for s, w in live["targets"].items() if w > 0}
    for name, x in v.items():
        assert sum(x["targets"].values()) == pytest.approx(1.0, abs=1e-6), name
        assert x["targets"].get("IBIT", 0) <= 0.05 + 1e-9, name
    assert "IBIT" not in v["No Bitcoin"]["targets"]
    gold = v["+ Gold (13 candidates)"]
    assert len(gold["shield_picks"]) >= 1 and sum(gold["targets"].values()) == pytest.approx(1.0)
    assert v["Core 50% SPY"]["targets"]["SPY"] >= 0.5
    assert v["Core 40% SPY / 10% AGG"]["targets"]["SPY"] >= 0.4
    sat = v["Bitcoin satellite"]
    assert "IBIT" not in sat["shield_picks"]
    assert sat["targets"].get("IBIT", 0) in (0, pytest.approx(0.05))
    row = out["months"][0]
    assert row["month"] == "2026-10" and row["complete"] is False
    assert set(row["returns_pct"]) == set(SCFG["variants"]) | {"60/40", "Live account"}
    log = (senv.mem / "SHADOW-LOG.md").read_text(encoding="utf-8")
    assert "2026-10 (to 2026-10-14)" in log and "Bitcoin satellite" in log


def test_month_completes_at_next_first_trading_day(senv):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    out = shadow.run(sargs(date="2026-11-03"))
    row = out["months"][0]
    assert row["complete"] is True and row["end"] == "2026-11-02"
    assert out["since_start"]["Live model"] == pytest.approx(row["returns_pct"]["Live model"])


def test_recorded_once_and_dry_run_writes_nothing(senv):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    assert shadow.run(sargs(date="2026-10-14", dry_run=True))["recorded"] == ["2026-09"]
    assert not (senv.mem / "shadow").exists() and not (senv.mem / "SHADOW-LOG.md").exists()
    shadow.run(sargs(date="2026-10-14"))
    first = (senv.mem / "shadow" / "2026-09.json").read_text()
    again = shadow.run(sargs(date="2026-10-20"))
    assert again["recorded"] is None
    assert (senv.mem / "shadow" / "2026-09.json").read_text() == first


def test_hold_and_since_start_math():
    p0 = pd.Series({"A": 100.0, "B": 50.0})
    p1 = pd.Series({"A": 110.0, "B": 50.0})
    r, drift = shadow._hold({"A": 0.5, "B": 0.5}, p0, p1)
    assert r == pytest.approx(0.05)
    assert drift["A"] == pytest.approx(0.55 / 1.05)
    rows = [{"returns_pct": {"x": 10.0}}, {"returns_pct": {"x": -10.0}}]
    assert shadow.since_start(rows)["x"] == pytest.approx(-1.0)
    assert shadow._turnover({"A": 1.0}, {}) == pytest.approx(1.0)


def test_backfills_every_missing_month(senv):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    raam.cmd_signal(args(date="2026-10-30"), CFG)
    out = shadow.run(sargs(date="2026-11-03"))
    assert out["recorded"] == ["2026-09", "2026-10"]
    assert [r["month"] for r in out["months"]] == ["2026-10", "2026-11"]
    assert out["months"][0]["complete"] and not out["months"][1]["complete"]


def test_variant_added_later_starts_its_own_since_start():
    rows = [{"returns_pct": {"old": 1.0, "new": None}}, {"returns_pct": {"old": 1.0, "new": 2.0}}]
    out = shadow.since_start(rows)
    assert out["old"] == pytest.approx(2.01) and out["new"] == pytest.approx(2.0)


def test_add_puts_the_candidate_in_the_universe():
    c = shadow.variant_cfg(CFG, {"add": ["GLD"]})
    assert c["universe"]["risk_assets"][-1] == "GLD"
    assert "GLD" not in CFG["universe"]["risk_assets"]          # the live config is untouched
