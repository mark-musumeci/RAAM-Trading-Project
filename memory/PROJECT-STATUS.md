# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-02
- Equity: $99,157.61 (day change: -1.106%)
- Drawdown: -1.91% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.52 | 50.0 | -0.48 |
| SGOV | 25.09 | 25.0 | 0.09 |
| DBC | 9.98 | 10.0 | -0.02 |
| VV | 9.93 | 10.0 | -0.07 |
| BTC | 4.98 | 5.0 | -0.02 |

- Alerts: none
- Timestamp: 2026-11-02 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
