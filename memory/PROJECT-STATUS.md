# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-27 (day after Thanksgiving, early-close session)
- Equity: $94,736.29 (day change: +1.48%)
- Drawdown: -6.29% | High-water mark: $101,092.20
- Circuit breaker: not tripped (thresholds: -20% drawdown, -5% daily)
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.28 | 50.0 | -0.72 |
| SGOV | 26.33 | 25.0 | 1.33 |
| VV | 10.08 | 10.0 | 0.08 |
| DBC | 9.51 | 10.0 | -0.49 |
| BTC | 4.07 | 5.0 | -0.93 |

- Alerts: none
- Note: no position fell more than 5%, so no research was run. Drawdown within the backtest's normal range. Signal: noop (last trading day is 2026-11-30). Review: noop (not first trading day).
- Timestamp: 2026-11-27 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
