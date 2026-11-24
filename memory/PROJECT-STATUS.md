# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-24
- Equity: $93,504.22 (day change: -1.20%)
- Drawdown: -7.51% | High-water mark: $101,092.20
- Circuit breaker: not tripped (thresholds: -20% drawdown, -5% daily)
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 48.94 | 50.0 | -1.06 |
| SGOV | 26.67 | 25.0 | 1.67 |
| VV | 10.08 | 10.0 | 0.08 |
| DBC | 9.47 | 10.0 | -0.53 |
| BTC | 4.12 | 5.0 | -0.88 |

- Alerts: none
- Note: estimated moves vs the 11-23 snapshot: QQQM ~-2.0%, BTC ~-2.3%, VV ~-0.5%, DBC ~-0.3%, SGOV flat. No position fell more than 5%, so no research was run. Drawdown -7.51% is within the backtest's normal range. Signal: not month-end (last trading day 2026-11-30). Review: noop (not first trading day).
- Timestamp: 2026-11-24 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
