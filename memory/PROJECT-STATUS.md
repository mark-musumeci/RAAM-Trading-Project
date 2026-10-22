# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-10-22
- Equity: $100,773.84 (day change: -0.343%)
- Drawdown: -0.315% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| SPY | 29.73 | 30.0 | -0.27 |
| AGG | 20.17 | 20.0 | 0.17 |
| BIL | 34.63 | 35.0 | -0.37 |
| DBC | 10.19 | 10.0 | 0.19 |
| IBIT | 4.78 | 5.0 | -0.22 |

- Alerts: none
- Timestamp: 2026-10-22 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
