# Trade Log

Append-only. Rows are written by `scripts/raam.py rebalance` and by `/trade` (manual). Never edit past rows.
- **Ref price** is the price seen when the order was planned, seconds before it was sent.
- **Slippage** is the fill price against the ref price, in basis points. Positive means a cost: paid more on a buy, or received less on a sell.

| Date | Symbol | Side | Filled qty | Avg fill price | Ref price | Slippage (bps) | Status | Reason |
|---|---|---|---|---|---|---|---|---|
| 2026-10-01 | AGG | buy | 211.477045696 | 94.1 | 94.115 | -1.6 | filled | RAAM rebalance (2026-09 signal) |
| 2026-10-01 | BIL | buy | 380.975713816 | 91.41 | 91.405 | 0.5 | filled | RAAM rebalance (2026-09 signal) |
| 2026-10-01 | DBC | buy | 305.965252152 | 32.52 | 32.5 | 6.2 | filled | RAAM rebalance (2026-09 signal) |
| 2026-10-01 | IBIT | buy | 104.692550505 | 47.52 | 47.57 | -10.5 | filled | RAAM rebalance (2026-09 signal) |
| 2026-10-01 | SPY | buy | 39.207450511 | 761.334635 | 761.31 | 0.3 | filled | RAAM rebalance (2026-09 signal) |
