---
description: Quick portfolio snapshot (read-only)
---
Read-only snapshot. No orders and no commits.

1. Run `python3 scripts/raam.py health --dry-run`. On Windows use `python`.
2. Show:
   - equity, cash, day change, drawdown, high-water mark and circuit-breaker state;
   - a table of each position with its weight %, target % and drift %;
   - the source of the targets.
3. Run `bash scripts/alpaca.sh orders open`. If any orders are open, list them.
4. Show the latest signal: the newest file in `memory/signals/`, with its month, targets and whether it has executed.
