# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-06
- Equity: $96,714.01 (day change: +0.52%)
- Drawdown: -4.33% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 48.76 | 50.0 | -1.24 |
| SGOV | 25.74 | 25.0 | 0.74 |
| DBC | 9.78 | 10.0 | -0.22 |
| VV | 9.96 | 10.0 | -0.04 |
| BTC | 5.05 | 5.0 | 0.05 |

- Alerts: none
- Timestamp: 2026-11-06 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
