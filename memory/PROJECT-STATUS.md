# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-12
- Equity: $100,980.73 (day change: +0.13%)
- Drawdown: 0.0% | High-water mark: $100,980.73
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 30.2 | 30.0 | 0.2 |
| AGG | 19.83 | 20.0 | -0.17 |
| BIL | 34.52 | 35.0 | -0.48 |
| DBC | 10.1 | 10.0 | 0.1 |
| IBIT | 4.85 | 5.0 | -0.15 |

- Alerts: none
- Timestamp: 2026-10-12 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
