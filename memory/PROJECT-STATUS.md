# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-26
- Equity: $100,790.88 (day change: +0.047%)
- Drawdown: -0.298% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 29.77 | 30.0 | -0.23 |
| AGG | 20.14 | 20.0 | 0.14 |
| BIL | 34.64 | 35.0 | -0.36 |
| DBC | 10.25 | 10.0 | 0.25 |
| IBIT | 4.7 | 5.0 | -0.3 |

- Alerts: none
- Timestamp: 2026-10-26 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
