# Project Status

## Current state
- Mode: **PAPER** (Alpaca paper account)
- Phase: live paper — first rebalance executed 2026-10-01 (inception); next signal 2026-10-30
- Circuit breaker: not tripped (source of truth: `memory/state.json`)

## Latest health
- Date: 2026-11-23
- Equity: $94,609.69 (day change: +3.75%)
- Drawdown: -6.41% | High-water mark: $101,092.20
- Circuit breaker: not tripped (thresholds: -20% drawdown, -5% daily)
- Positions:

| Symbol | Weight % | Target % | Drift % |
|---|---|---|---|
| QQQM | 49.36 | 50.0 | -0.64 |
| SGOV | 26.35 | 25.0 | 1.35 |
| VV | 10.01 | 10.0 | 0.01 |
| DBC | 9.39 | 10.0 | -0.61 |
| BTC | 4.17 | 5.0 | -0.83 |

- Alerts: none
- Note: strong rebound day after Friday's -3.00%. Estimated moves vs the 11-20 snapshot: QQQM ~+5.8%, VV ~+4.6%, BTC ~+3.9%, DBC ~-0.5%. No position fell more than 5%. A quick web search found no dated coverage of today's rally, so the cause is unconfirmed (context only, no action). Drawdown -6.41% is within the backtest's normal range. Signal: not month-end (last trading day 2026-11-30). Review: noop (not first trading day).
- Timestamp: 2026-11-23 UTC

## Milestones
- [x] 2026-09-23 Repo scaffolded, engine + tests written
- [x] 2026-09-23 API keys added to cloud environment
- [x] 2026-09-23 Routines created and first manual runs verified
- [x] 2026-09-30 First live-paper month-end signal
- [x] 2026-10-01 First paper rebalance executed
- [ ] Historical backtest to settle paper ambiguities
