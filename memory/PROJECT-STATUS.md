# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-25
- Equity: $93,295.37 (day change: -0.30%)
- Drawdown: -7.71% | High-water mark: $101,092.20
- Circuit breaker: not tripped (thresholds: -20% drawdown, -5% daily)
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 48.72 | 50.0 | -1.28 |
| SGOV | 26.73 | 25.0 | 1.73 |
| VV | 10.07 | 10.0 | 0.07 |
| DBC | 9.57 | 10.0 | -0.43 |
| BTC | 4.17 | 5.0 | -0.83 |

- Alerts: none
- Note: estimated moves vs the 11-24 snapshot: QQQM ~-0.7%, VV ~-0.3%, BTC ~+1.0%, DBC ~+0.8%, SGOV flat. No position fell more than 5%, so no research was run. Drawdown -7.71% is within the backtest's normal range. Signal: not month-end (last trading day 2026-11-30). Review: noop (not first trading day).
- Timestamp: 2026-11-25 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
