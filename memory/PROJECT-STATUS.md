# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-13
- Equity: $97,726.10 (day change: -1.26%)
- Drawdown: -3.33% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.59 | 50.0 | -0.41 |
| SGOV | 25.49 | 25.0 | 0.49 |
| DBC | 9.61 | 10.0 | -0.39 |
| VV | 10.12 | 10.0 | 0.12 |
| BTC | 4.49 | 5.0 | -0.51 |

- Alerts: none
- Timestamp: 2026-11-13 21:43 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
