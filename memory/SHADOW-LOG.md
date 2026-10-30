# Shadow Variants (tracked, never traded)

Written by `scripts/shadow.py`; do not hand-edit. Variants are pre-registered in `config/shadow.json` (owner decision 2026-10-14). **Context only:** nothing here changes the live strategy; any change is an owner decision at a checkpoint (see `memory/EVALUATION-PLAN.md`).

Variant returns run from the open of the month's first trading day to the open of the next month's first trading day, after 5 bps per side on turnover. The current month is to date. *Live account* is the real paper account (close-to-close equity, after real costs). Its gap to *Live model* is the replication check (evaluation B4).

| Month | Live account | Live model | Previous live (60/40 Core) | No Bitcoin | Core 50% SPY | Core 40% SPY / 10% AGG | Bitcoin satellite | + Gold (13 candidates) | 60/40 |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10 (to 2026-10-30) | +0.30% | +0.21% | n/a | +0.47% | −0.53% | −0.16% | +0.02% | n/a | +0.29% |
| **Since start** | **+0.30%** | **+0.21%** | **n/a** | **+0.47%** | **−0.53%** | **−0.16%** | **+0.02%** | **n/a** | **+0.29%** |

*Since start* compounds each column from its first tracked month; n/a = not yet tracked.

## What each variant held

### 2026-11 (signal 2026-10-30, recorded 2026-10-30)

| Variant | Holdings |
|---|---|
| Live model | QQQM 50%, SGOV 25%, DBC 10%, VV 10%, BTC 5% |
| Previous live (60/40 Core) | SPY 30%, SGOV 25%, AGG 20%, DBC 10%, VV 10%, BTC 5% |
| No Bitcoin | QQQM 50%, SGOV 30%, DBC 10%, VV 10% |
| Core 50% SPY | SPY 50%, SGOV 25%, DBC 10%, VV 10%, BTC 5% |
| Core 40% SPY / 10% AGG | SPY 40%, SGOV 25%, AGG 10%, DBC 10%, VV 10%, BTC 5% |
| Bitcoin satellite | QQQM 50%, SGOV 27%, DBC 9%, VV 9%, BTC 5% |
| + Gold (13 candidates) | QQQM 50%, SGOV 25%, DBC 10%, VV 10%, BTC 5% |

### 2026-10 (signal 2026-09-30, recorded 2026-10-14)

| Variant | Holdings |
|---|---|
| Live model | BIL 35%, SPY 30%, AGG 20%, DBC 10%, IBIT 5% |
| No Bitcoin | BIL 30%, SPY 30%, AGG 20%, DBC 10%, VV 10% |
| Core 50% SPY | SPY 50%, BIL 35%, DBC 10%, IBIT 5% |
| Core 40% SPY / 10% AGG | SPY 40%, BIL 35%, AGG 10%, DBC 10%, IBIT 5% |
| Bitcoin satellite | SPY 30%, BIL 27%, AGG 20%, DBC 9%, VV 9%, IBIT 5% |

## Variant definitions

- **Live model:** The live rules recomputed by the engine (uses the live signal file when it exists). Checks that the account tracks the model (evaluation B4).
- **Previous live (60/40 Core):** The strategy before 2026-10-14: fixed 30% SPY + 20% AGG Core with the same Shield. Shows month by month whether the QQQM trend Core is paying off.
- **No Bitcoin:** How much of the result is Bitcoin (IBIT until October 2026, BTC from November).
- **Core 50% SPY:** Owner proposal 2026-10-14: growth-only Core (backtest 11.8%/yr, Sharpe 1.14, 2008 -18%).
- **Core 40% SPY / 10% AGG:** Middle ground between the live Core and the 50% SPY Core.
- **Bitcoin satellite:** Bitcoin (BTC) outside the ranking: 5% Bitcoin (BTC) when its momentum beats cash, else cash; the Shield (45%) ranks the other 11. Removes the half-empty Bitcoin (BTC) slot.
- **+ Gold (13 candidates):** Owner decision 2026-10-14: GLD as an ordinary 13th Shield candidate (Bitcoin keeps its 5% cap). Tracked from the 2026-10 signal (November). Planned for adoption at the 3-month checkpoint (Jan 2027). Backtest 2015-26: 9.4%/yr, Sharpe vs T-bills 0.97 vs 0.93 live; 2008-26 without Bitcoin: worse crash tail (worst month-end -23.5% vs -19.0%).
