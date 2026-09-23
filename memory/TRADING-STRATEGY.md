# Trading Strategy — Ranked Asset Allocation Model (RAAM)

Source: Gioele Giordano, *Ranked Asset Allocation Model*, 2018 Charles H. Dow Award (CMT Association).
Parameters live in [`config/raam.json`](../config/raam.json); the engine is [`scripts/raam.py`](../scripts/raam.py).
**This file describes the rules. Claude never changes the rules during a routine run.** Changes happen
only when the owner decides them, and they are recorded in the change log at the bottom.

## Universe (7Twelve portfolio, 12 ETFs)

| Asset class | ETFs |
|---|---|
| US Equities | VV, IJH, IJR |
| International Equities | EFA, EEM |
| Real Estate | RWR |
| Commodities / Natural Resources | DBC, VAW |
| US Bonds / Inflation-protected | AGG, TIP |
| International Bonds | IGOV |
| Cash | SHY (not ranked; receives weight from excluded slots) |

## Factors
Computed daily from Alpaca daily bars (split- and dividend-adjusted). The ranking uses only the value from the **last trading day of the month**.

| Factor | Definition | Rank 1 goes to |
|---|---|---|
| **M**: Absolute Momentum | 4-month (84 sessions) rate of change, % | highest momentum |
| **V**: Volatility Model | RiskMetrics EWMA volatility, λ = 0.94, annualized, with a 10-day SMA smoothing | lowest volatility |
| **C**: Average Relative Correlation | mean pairwise correlation of daily returns with the other 10 ETFs over 84 sessions | lowest correlation |
| **T**: ATR Trend/Breakout | +2 after the high breaks the upper band, −2 after the low breaks the lower band. It changes the session *after* the break | — |

Bands:
- Upper = highest close(63) + ATR(42).
- Lower = highest low(105) − ATR(42). This is our interpretation; see A3.

## Ranking and allocation
1. Rank the 11 non-cash ETFs from 1 to 11 on each of M, V and C.
2. `Score = wM·Rank(M) + wV·Rank(V) + wC·Rank(C) − T − M/x`
   - Lower is better.
   - The `−T` term rewards up-trends.
   - The `−M/x` term only breaks ties, in favour of higher momentum.
3. Take the **5 lowest scores**. Each gets **20%**.
4. Any of those 5 with **momentum ≤ 0** has its 20% moved to **SHY**. If all 5 are negative, the portfolio is 100% SHY.
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
- Target weights must sum to 100% ±0.5%. Only universe tickers may be traded, and a single risk-asset buy is capped at 25% of equity.
- **Circuit breaker:** it trips on a −15% drawdown from the high-water mark, or a −5% single day. The next morning run moves the portfolio to 100% SHY and it stays there until the owner resets it by setting `circuit_breaker.tripped` to `false` in `memory/state.json`.
- Stale or missing data for any ETF halts the signal. There is no guessing.

## Change log
| Date | Change | Decided by |
|---|---|---|
| 2026-09-23 | Initial setup with the defaults above | owner |
