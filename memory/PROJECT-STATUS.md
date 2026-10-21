# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-21
- Equity: $101,075.85 (day change: +0.223%)
- Drawdown: -0.016% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 29.98 | 30.0 | -0.02 |
| AGG | 19.89 | 20.0 | -0.11 |
| BIL | 34.52 | 35.0 | -0.48 |
| DBC | 10.14 | 10.0 | 0.14 |
| IBIT | 4.97 | 5.0 | -0.03 |

- Alerts: none
- Timestamp: 2026-10-21 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
