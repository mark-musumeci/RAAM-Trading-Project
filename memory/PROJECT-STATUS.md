# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-16
- Equity: $96,259.21 (day change: -1.92%)
- Drawdown: -4.78% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.37 | 50.0 | -0.63 |
| SGOV | 25.88 | 25.0 | 0.88 |
| DBC | 9.59 | 10.0 | -0.41 |
| VV | 10.08 | 10.0 | 0.08 |
| BTC | 4.37 | 5.0 | -0.63 |

- Alerts: none
- Note: BTC -5.2% today (QQQM -2.7%, VV -1.9%, DBC -1.8%). Quick research found no fund-specific or structural news; the drop looks like part of a broad risk-off day. Context only, no action.
- Timestamp: 2026-11-16 21:44 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
