# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-10
- Equity: $98,111.57 (day change: -0.36%)
- Drawdown: -2.95% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.50 | 50.0 | -0.50 |
| SGOV | 25.38 | 25.0 | 0.38 |
| DBC | 9.56 | 10.0 | -0.44 |
| VV | 10.02 | 10.0 | 0.02 |
| BTC | 4.84 | 5.0 | -0.16 |

- Alerts: none
- Timestamp: 2026-11-10 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
