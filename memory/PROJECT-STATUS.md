# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-03
- Equity: $99,624.65 (day change: +0.65%)
- Drawdown: -1.45% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.64 | 50.0 | -0.36 |
| SGOV | 24.97 | 25.0 | -0.03 |
| DBC | 9.93 | 10.0 | -0.07 |
| VV | 9.92 | 10.0 | -0.08 |
| BTC | 5.04 | 5.0 | 0.04 |

- Alerts: none
- Timestamp: 2026-11-03 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
