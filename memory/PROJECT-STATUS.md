# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-07
- Equity: $100,544.76 (day change: -0.37%)
- Drawdown: -0.39% | High-water mark: $100,942.78
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 30.31 | 30.0 | 0.31 |
| AGG | 19.75 | 20.0 | -0.25 |
| BIL | 34.65 | 35.0 | -0.35 |
| DBC | 9.89 | 10.0 | -0.11 |
| IBIT | 4.9 | 5.0 | -0.1 |

- Alerts: none
- Timestamp: 2026-10-07 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
