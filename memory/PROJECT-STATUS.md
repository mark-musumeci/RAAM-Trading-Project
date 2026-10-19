# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-19
- Equity: $100,631.84 (day change: -0.005%)
- Drawdown: -0.46% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 29.88 | 30.0 | -0.12 |
| AGG | 19.99 | 20.0 | -0.01 |
| BIL | 34.67 | 35.0 | -0.33 |
| DBC | 10.14 | 10.0 | 0.14 |
| IBIT | 4.83 | 5.0 | -0.17 |

- Alerts: none
- Timestamp: 2026-10-19 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
