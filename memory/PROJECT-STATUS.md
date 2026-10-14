# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-14
- Equity: $100,593.86 (day change: -0.48%)
- Drawdown: -0.49% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 29.96 | 30.0 | -0.04 |
| AGG | 19.93 | 20.0 | -0.07 |
| BIL | 34.66 | 35.0 | -0.34 |
| DBC | 10.13 | 10.0 | 0.13 |
| IBIT | 4.81 | 5.0 | -0.19 |

- Alerts: none
- Timestamp: 2026-10-14 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
