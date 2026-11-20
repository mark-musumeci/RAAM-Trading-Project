# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-20
- Equity: $91,527.24 (day change: -3.00%)
- Drawdown: -9.46% | High-water mark: $101,092.20
- Circuit breaker: not tripped (thresholds: -20% drawdown, -5% daily)
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 48.23 | 50.0 | -1.77 |
| SGOV | 27.23 | 25.0 | 2.23 |
| VV | 9.89 | 10.0 | -0.11 |
| DBC | 9.75 | 10.0 | -0.25 |
| BTC | 4.15 | 5.0 | -0.85 |

- Alerts: none
- Note: no position moved more than 5% today (est. vs yesterday's snapshot: QQQM ~-4.3%, BTC ~-4.2%, VV ~-3.5%, DBC ~-1.2%). Drawdown -9.46% is within the backtest's normal range (worst month-end -11.7%). Signal: not month-end (last trading day 2026-11-30). Review: noop (not first trading day).
- Timestamp: 2026-11-20 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
