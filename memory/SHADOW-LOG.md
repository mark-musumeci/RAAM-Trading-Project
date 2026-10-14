# Shadow Variants (tracked, never traded)

Written by `scripts/shadow.py`; do not hand-edit. Variants are pre-registered in `config/shadow.json` (owner decision 2026-10-14). **Context only:** nothing here changes the live strategy; any change is an owner decision at a checkpoint (see `memory/EVALUATION-PLAN.md`).

Variant returns run from the open of the month's first trading day to the open of the next month's first trading day, after 5 bps per side on turnover. The current month is to date. *Live account* is the real paper account (close-to-close equity, after real costs). Its gap to *Live model* is the replication check (evaluation B4).

| Month | Live account | Live model | No Bitcoin | Core 50% SPY | Core 40% SPY / 10% AGG | Bitcoin satellite | 60/40 |
|---|---|---|---|---|---|---|---|
| 2026-10 (to 2026-10-14) | +1.08% | +0.57% | +0.73% | +0.52% | +0.54% | +0.58% | +0.73% |
| **Since start** | **+1.08%** | **+0.57%** | **+0.73%** | **+0.52%** | **+0.54%** | **+0.58%** | **+0.73%** |

## What each variant held

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
- **No Bitcoin:** How much of the result is IBIT.
- **Core 50% SPY:** Owner proposal 2026-10-14: growth-only Core (backtest 11.8%/yr, Sharpe 1.14, 2008 -18%).
- **Core 40% SPY / 10% AGG:** Middle ground between the live Core and the 50% SPY Core.
- **Bitcoin satellite:** IBIT outside the ranking: 5% IBIT when its momentum beats cash, else BIL; the Shield (45%) ranks the other 11. Removes the half-empty IBIT slot.
