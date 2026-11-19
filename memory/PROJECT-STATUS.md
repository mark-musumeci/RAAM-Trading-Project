# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-19
- Equity: $94,101.18 (day change: -1.54%)
- Drawdown: -6.92% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.00 | 50.0 | -1.00 |
| SGOV | 26.48 | 25.0 | 1.48 |
| VV | 9.97 | 10.0 | -0.03 |
| DBC | 9.60 | 10.0 | -0.40 |
| BTC | 4.21 | 5.0 | -0.79 |

- Alerts: none
- Note: no position moved more than 5% today (est. vs yesterday's snapshot: QQQM ~-2.7%, VV ~-1.9%, BTC ~-1.4%, DBC ~-0.9%). Signal: not month-end (last trading day 2026-11-30). Review: noop (not first trading day).
- Timestamp: 2026-11-19 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
