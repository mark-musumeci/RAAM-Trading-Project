# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-05
- Equity: $95,865.12 (day change: -3.96%)
- Drawdown: -5.17% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 48.38 | 50.0 | -1.62 |
| SGOV | 25.96 | 25.0 | 0.96 |
| DBC | 10.03 | 10.0 | 0.03 |
| VV | 10.02 | 10.0 | 0.02 |
| BTC | 5.10 | 5.0 | 0.10 |

- Alerts: none
- Note: large down day; web search found no coverage explaining the cause (context only, no action).
- Timestamp: 2026-11-05 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
