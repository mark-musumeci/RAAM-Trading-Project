# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-09
- Equity: $98,489.91 (day change: +1.69%)
- Drawdown: -2.57% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.52 | 50.0 | -0.48 |
| SGOV | 25.28 | 25.0 | 0.28 |
| DBC | 9.60 | 10.0 | -0.40 |
| VV | 10.02 | 10.0 | 0.02 |
| BTC | 4.89 | 5.0 | -0.11 |

- Alerts: none
- Timestamp: 2026-11-09 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
