# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-09
- Equity: $100,859.06 (day change: +0.24%)
- Drawdown: -0.08% | High-water mark: $100,942.78
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 30.26 | 30.0 | 0.26 |
| AGG | 19.83 | 20.0 | -0.17 |
| BIL | 34.57 | 35.0 | -0.43 |
| DBC | 10.0 | 10.0 | 0.0 |
| IBIT | 4.85 | 5.0 | -0.15 |

- Alerts: none
- Timestamp: 2026-10-09 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
