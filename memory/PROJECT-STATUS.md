# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-26 (Thanksgiving — US market holiday, no trading session)
- Equity: $93,353.75 (day change: 0.00%)
- Drawdown: -7.66% | High-water mark: $101,092.20
- Circuit breaker: not tripped (thresholds: -20% drawdown, -5% daily)
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 48.77 | 50.0 | -1.23 |
| SGOV | 26.71 | 25.0 | 1.71 |
| VV | 10.06 | 10.0 | 0.06 |
| DBC | 9.56 | 10.0 | -0.44 |
| BTC | 4.16 | 5.0 | -0.84 |

- Alerts: none
- Note: market closed for Thanksgiving; the small equity change vs 11-25 ($93,295 → $93,354) is a mark-to-market quote refresh, not trading. No position fell more than 5%, so no research was run. Drawdown within the backtest's normal range. Signal: not month-end (last trading day 2026-11-30). Review: noop (not first trading day).
- Timestamp: 2026-11-26 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
