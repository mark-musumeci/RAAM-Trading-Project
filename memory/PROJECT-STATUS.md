# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-17
- Equity: $95,794.87 (day change: -0.47%)
- Drawdown: -5.24% | High-water mark: $101,092.20
- Circuit breaker: not tripped
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.32 | 50.0 | -0.68 |
| SGOV | 26.01 | 25.0 | 1.01 |
| DBC | 9.61 | 10.0 | -0.39 |
| VV | 10.02 | 10.0 | 0.02 |
| BTC | 4.33 | 5.0 | -0.67 |

- Alerts: none
- Note: no position moved more than 5% today (BTC roughly -1.4% by market value). Signal: not month-end (last trading day 2026-11-30). Review: noop (not first trading day).
- Timestamp: 2026-11-17 21:43 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
