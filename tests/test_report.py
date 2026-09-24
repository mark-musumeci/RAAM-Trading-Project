"""Tests for scripts/report.py against a fake Alpaca (no network)."""
import datetime as dt
import json
import pathlib
import re
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import raam  # noqa: E402
import report  # noqa: E402
from test_commands import CFG, FakeAlpaca, args, env  # noqa: E402,F401  (env is a fixture)


class FakeWithHistory(FakeAlpaca):
    def portfolio_history(self, start, end):
        days = pd.bdate_range(start, end)
        rng = np.random.default_rng(5)
        eq = 100_000 * np.cumprod(1 + rng.normal(0.0003, 0.004, len(days)))
        ts = [int(dt.datetime.combine(d.date(), dt.time(16), raam.ET).timestamp()) for d in days]
        return {"timestamp": ts, "equity": list(eq)}


@pytest.fixture
def renv(env):
    fake = FakeWithHistory()
    env.mp.setattr(raam, "Alpaca", lambda: fake)
    env.fake = fake
    return env


def run(argv, capsys):
    code = report.main(argv)
    return code, json.loads(capsys.readouterr().out)


def test_noop_when_not_last_trading_day(renv, capsys):
    code, out = run(["--date", "2026-09-15"], capsys)
    assert code == 0 and out["status"] == "noop"


def test_metrics_only_keys_and_benchmarks(renv, capsys):
    code, out = run(["--date", "2026-09-30", "--metrics-only"], capsys)
    assert code == 0 and out["status"] == "ok"
    m = out["metrics"]
    for k in ("month_return_pct", "benchmarks_month_pct", "vs_6040_month_pct", "since_inception_pct",
              "max_drawdown_pct", "holdings", "next_allocation", "checks"):
        assert k in m
    assert m["benchmarks_month_pct"]["60/40"] is not None
    assert m["holdings"] == []                 # nothing executed yet: first month
    assert m["invested"] is False and m["inception"] is None
    assert m["month_return_pct"] is None and m["vs_6040_month_pct"] is None   # no fake "beat 60/40"
    assert m["checks"][0]["status"] == "na"
    assert len(m["checks"]) == 4
    assert not (raam.ROOT / "reports").exists()


def test_full_report_is_one_page_pdf_with_next_allocation(renv, capsys, tmp_path):
    raam.cmd_signal(args(date="2026-09-30"), CFG)            # next month's plan exists
    notes = tmp_path / "notes.txt"
    notes.write_text("- First bullet.\n- Second bullet.\n- Third bullet.\n- Fourth is dropped.\n")
    code, out = run(["--date", "2026-09-30", "--notes-file", str(notes)], capsys)
    assert code == 0 and out["status"] == "ok", out
    pdf = raam.ROOT / out["file"]
    data = pdf.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(re.findall(rb"/Type\s*/Page(?!s)", data)) == 1
    alloc = {r["symbol"]: r for r in out["metrics"]["next_allocation"]}
    assert alloc["SPY"]["core_pct"] == pytest.approx(30.0)
    assert sum(r["total_pct"] for r in alloc.values()) == pytest.approx(100.0, abs=0.5)


def test_holdings_after_executed_rebalance(renv, capsys):
    raam.cmd_signal(args(date="2026-09-30"), CFG)
    raam.cmd_rebalance(args(date="2026-10-01"), CFG)
    renv.mp.setattr(raam, "today_et", lambda: dt.date(2026, 10, 30))
    code, out = run(["--month", "2026-10", "--metrics-only"], capsys)
    assert code == 0, out
    rows = {r["symbol"]: r for r in out["metrics"]["holdings"]}
    assert rows["SPY"]["sleeve"] in ("Core", "Core + Shield")
    assert sum(r["weight_pct"] for r in rows.values()) == pytest.approx(100.0, abs=0.5)
    assert out["metrics"]["inception"] == "2026-10-01" and out["metrics"]["invested"] is True


def test_missing_notes_file_still_renders(renv, capsys):
    code, out = run(["--date", "2026-09-30", "--notes-file", "does-not-exist.txt"], capsys)
    assert code == 0 and out["status"] == "ok"
