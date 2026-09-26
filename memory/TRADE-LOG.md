# Trade Log

Append-only. Rows are written by `scripts/raam.py rebalance` and by `/trade` (manual). Never edit past rows.
- **Ref price** is the price seen when the order was planned, seconds before it was sent.
- **Slippage** is the fill price against the ref price, in basis points. Positive means a cost: paid more on a buy, or received less on a sell.

| Date | Symbol | Side | Filled qty | Avg fill price | Ref price | Slippage (bps) | Status | Reason |
|---|---|---|---|---|---|---|---|---|
