# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-20
- Equity: $100,986.17 (day change: +0.281%)
- Drawdown: -0.105% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 29.95 | 30.0 | -0.05 |
| AGG | 19.97 | 20.0 | -0.03 |
| BIL | 34.55 | 35.0 | -0.45 |
| DBC | 10.17 | 10.0 | 0.17 |
| IBIT | 4.86 | 5.0 | -0.14 |

- Alerts: none
- Timestamp: 2026-10-20 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
