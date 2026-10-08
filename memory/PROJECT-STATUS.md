# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-08
- Equity: $100,602.41 (day change: -0.05%)
- Drawdown: -0.34% | High-water mark: $100,942.78
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 30.16 | 30.0 | 0.16 |
| AGG | 19.88 | 20.0 | -0.12 |
| BIL | 34.64 | 35.0 | -0.36 |
| DBC | 10.01 | 10.0 | 0.01 |
| IBIT | 4.81 | 5.0 | -0.19 |

- Alerts: none
- Timestamp: 2026-10-08 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
