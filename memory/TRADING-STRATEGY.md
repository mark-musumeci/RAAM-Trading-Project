# Trading Strategy — Core & Shield

The portfolio has two halves:
- **Core**, 50%: a fixed 60/40 (30% SPY + 20% AGG) that does the growing.
- **Shield**, 50%: the Ranked Asset Allocation Model (RAAM), which does the defending.

RAAM source: Gioele Giordano, *Ranked Asset Allocation Model*, 2018 Charles H. Dow Award (CMT Association).
Parameters live in [`config/raam.json`](../config/raam.json); the engine is [`scripts/raam.py`](../scripts/raam.py).
**This file describes the rules. Claude never changes the rules during a routine run.** Changes happen
only when the owner decides them, and they are recorded in the change log at the bottom.

## Portfolio structure: Core & Shield
| Half | Weight | Holdings | Rule |
|---|---|---|---|
| **Core** | 50% | **SPY 30% + AGG 20%** | Fixed, and reset to these weights at every monthly rebalance |
| **Shield** | 50% | RAAM: 5 slots of **10% of the portfolio** each, from the 11 ETFs below, with BIL for failed slots | RAAM rules below; the monthly signal decides it |

- Portfolio targets = Core weights + 0.5 × RAAM (Shield) weights. For example, if RAAM picks AGG, total AGG is 20% + 10% = 30%.
- Configured in `config/raam.json → portfolio`. Setting `core: {}` and `shield_weight: 1.0` runs RAAM alone.
- Why: RAAM alone is a strong defender but lags badly in bull markets. The Core supplies growth, and the Shield roughly halves the damage in slow bear markets. See `memory/BACKTEST-SUMMARY.md`.

## Shield universe (7Twelve portfolio + IBIT: 12 ranked candidates, plus BIL as cash)

| Asset class | ETFs |
|---|---|
| US Equities | VV, IJH, IJR |
| International Equities | EFA, EEM |
| Real Estate | RWR |
| Commodities / Natural Resources | DBC, VAW |
| US Bonds / Inflation-protected | AGG, TIP |
| International Bonds | IGOV |
| Crypto | **IBIT**, iShares spot-Bitcoin ETF. Added 2026-09-26. **Capped at 5% of the whole portfolio** (`portfolio.max_weight`); any excess goes to BIL. |
| Cash | **BIL**, 1–3 month T-bills (not ranked; receives weight from excluded slots). The paper and 7Twelve use SHY; replaced by Tier 1 upgrade U2. |

## Factors
Computed daily from Alpaca daily bars (split- and dividend-adjusted). The ranking uses only the value from the **last trading day of the month**.

| Factor | Definition | Rank 1 goes to |
|---|---|---|
| **M**: Absolute Momentum | 4-month (84 sessions) rate of change, % | highest momentum |
| **V**: Volatility Model | RiskMetrics EWMA volatility, λ = 0.94, annualized, with a 10-day SMA smoothing | lowest volatility |
| **C**: Average Relative Correlation | mean pairwise correlation of daily returns with the other 10 ETFs over 84 sessions | lowest correlation |
| **T**: ATR Trend/Breakout | +2 after the high breaks the upper band, −2 after the low breaks the lower band. It changes the session *after* the break. **Informational only: not scored since improvement A (`w_trend` = 0)** | — |

Bands:
- Upper = highest close(63) + ATR(42).
- Lower = highest low(105) − ATR(42). This is our interpretation; see A3.

## Ranking and allocation
1. Rank the 12 non-cash candidates from 1 to 12 on each of M, V and C.
2. `Score = wM·Rank(M) + wV·Rank(V) + wC·Rank(C) − w_trend·T − M/x`
   - Lower is better.
   - **`w_trend` = 0 (improvement A):** the paper's `−T` trend bonus is switched off. T is still computed and shown in the signal log. Setting `w_trend` to 1 restores the paper's rule.
   - The `−M/x` term only breaks ties, in favour of higher momentum.
3. Take the **5 lowest scores**. Each gets **20% of the Shield**, which is 10% of the portfolio.
4. **Cash hurdle (Tier 1 upgrade U1):** each of those 5 keeps its 20% only if its momentum **beats the cash asset's own 4-month momentum**. Otherwise its slot moves to **BIL**. If none beat cash, the whole Shield is BIL (50% of the portfolio) while the Core stays invested. The paper's rule was momentum > 0%.
5. **Timing:** the signal is computed after the close on the last trading day of month *m*. It is executed at about 09:45 ET on the first trading day of month *m+1*. It is held all month; there are no stops and no intra-month trading.

## Open ambiguities in the paper (defaults in use)

| # | Issue | Current default | Alternatives in config |
|---|---|---|---|
| A1 | wM, wV, wC and x are never disclosed | equal weights of 1/3 each; x = 1000 | any weights |
| A2 | The rank direction contradicts itself: the text says high momentum means a high rank, but the lowest total is selected | `1_is_best`, with lowest score selected | — |
| A3 | The lower band is written as "ATR + highest low(105)", which would sit above price in an uptrend | `hhv_low_minus_atr` | `hhv_low_plus_atr` (literal reading) |
| A4 | The "edited GARCH using OHLC" formula is not specified | `close` (close-to-close EWMA) | `parkinson`, `garman_klass` |
| A5 | The `+M/x` tie-breaker sign conflicts with lower-is-better | `tiebreak_sign = -1` | `+1` (literal) |
| A6 | Tied factor values | average rank | — |
| A7 | The paper's backtest (+638%, Sharpe 1.94) is in-sample, has no costs, and IGOV was interpolated before 2009 | treat its claims as optimistic | — |

## Guardrails (not part of the paper)
- **Paper trading only**, unless `PAPER_TRADING=false` **and** `LIVE_CONFIRM=yes`.
- Target weights must sum to 100% ±0.5%. Only universe tickers may be traded, and a single non-cash buy is capped at **35%** of equity. It was 25%; it was raised because Core positions reach 30% (SPY, or AGG when RAAM also picks it).
- **Circuit breaker (Tier 1 upgrade U3):**
  - It trips on a **−20%** drawdown of the **whole portfolio** from its high-water mark, or a −5% single day. The next morning run moves the whole portfolio, Core included, to 100% BIL.
  - It **re-enters automatically** at the next monthly rebalance, following a signal computed after the trip, and re-bases the high-water mark at that point.
  - Setting `circuit_breaker_reset` to `manual` in config restores the old behaviour: stay in cash until the owner resets `memory/state.json`.
  - Backtest behaviour: Core & Shield never tripped it in 2009–2026 (worst −14.6%). In the 2008 stress test it tripped once, on 2009-02-23 at −20.2%, and re-entered at the March rebalance. It is a tail-risk safety net.
- Stale or missing data for any ETF halts the signal. There is no guessing.

## Change log
| Date | Change | Decided by |
|---|---|---|
| 2026-09-23 | Initial setup with the defaults above | owner |
| 2026-09-23 | **Tier 1 upgrades:** U1 cash-momentum hurdle (was >0%); U2 BIL replaces SHY as cash; U3 breaker −20% with auto re-entry (was −15%, manual reset). Backtest in `memory/BACKTEST-SUMMARY.md`. | owner |
| 2026-09-23 | **Improvement A:** ATR trend term removed from the score (`w_trend` 0). Three separate backtests agreed. 2009–26: CAGR 4.1% → 4.7%, daily max DD −16.2% → −12.0%, down capture 30% → 24%. It improved both 2009–19 and 2020–now. | owner |
| 2026-09-26 | **IBIT added** as the 12th Shield candidate, **capped at 5% of the portfolio**. Adopted before the first trade. Evidence (2015–26, with BTC-USD as a stand-in and a 0.25% fee): CAGR 6.6% → 9.5%, Sharpe vs T-bills 0.63 → 0.95, worst drop −14.6% → −14.1%. Better in all three sub-periods. About half the gain survives with Bitcoin flattened to a 0% long-run return. Costs: 2018 −6.4% vs −3.1%. | owner |
| 2026-09-24 | **Core & Shield:** 50% fixed 60/40 Core (30% SPY + 20% AGG) + 50% RAAM Shield. Per-order cap raised 25% → 35%. 2009–26 backtest: CAGR 7.5%, Sharpe 1.11 (60/40 1.09), max DD −11.1% month-end / −14.6% daily (60/40 −19.2% month-end), 2022 −7.8% (60/40 −15.2%). | owner |
