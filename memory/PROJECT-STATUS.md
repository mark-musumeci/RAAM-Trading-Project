# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-04
- Equity: $99,932.40 (day change: +0.54%)
- Drawdown: -1.15% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.83 | 50.0 | -0.17 |
| SGOV | 24.90 | 25.0 | -0.10 |
| DBC | 9.55 | 10.0 | -0.45 |
| VV | 10.05 | 10.0 | 0.05 |
| BTC | 5.17 | 5.0 | 0.17 |

- Alerts: none
- Timestamp: 2026-11-04 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
