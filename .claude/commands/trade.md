---
description: Manual trade helper — /trade <symbol> <qty> <buy|sell> (interactive use only)
argument-hint: "<symbol> <qty> <buy|sell>"
---
Manual trade: `$ARGUMENTS`

**Interactive use only.** If this is running inside a scheduled routine, refuse and stop.

1. Parse the symbol, quantity and side. The symbol must be in the RAAM universe (see `config/raam.json`). `alpaca.sh` enforces this too.
2. Show the current position, the latest quote (`bash scripts/alpaca.sh quote SYM`) and the estimated order value.
3. Warn that manual trades make the portfolio drift from the RAAM targets. The next monthly rebalance will correct the drift.
4. **Ask for explicit confirmation** before placing the order.
5. On confirmation:
   - run `bash scripts/alpaca.sh order SYM QTY SIDE`;
   - poll `bash scripts/alpaca.sh orders closed` until the order fills;
   - append a row to `memory/TRADE-LOG.md` with reason `manual`;
   - commit and push.
