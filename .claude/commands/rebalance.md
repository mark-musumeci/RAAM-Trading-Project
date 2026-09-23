---
description: Execute last month-end's RAAM signal on the first trading day (also handles circuit breaker → BIL and its auto re-entry)
argument-hint: "[dry_run] [force] [force_date=YYYY-MM-DD] [confirm_live_force]"
---
Monthly rebalance. Follow the SOP in CLAUDE.md.

1. Run `python3 scripts/raam.py rebalance`, with flags from `$ARGUMENTS`:
   - `dry_run` → `--dry-run`;
   - `force_date=D` → `--date D`;
   - `force` → `--force`, but ONLY together with `--dry-run`, unless `confirm_live_force` is also present.

   The script decides by itself whether today is a rebalance day. It also always acts if the circuit breaker is tripped.
2. Handle the result:
   - `noop` → nothing to do. Reply with the reason. Send **no** Discord message, and skip the commit if nothing changed.
   - `ok` with `dry_run` → report the planned orders and send the Discord message `RAAM DRY RUN rebalance: <orders>`.
   - `ok` with fills → check every order has status `filled`. Send the Discord message `RAAM rebalanced (<reason>): SELL ..., BUY ... | all filled`.
   - `halt` / `error` → Discord message `RAAM ⚠️ rebalance halted: <reason>`. **Do not** retry, place manual orders or "fix" anything. The owner decides.
3. After a real (non-dry-run) rebalance, run `python3 scripts/raam.py health` so that `state.json` reflects the new positions.
4. Commit and push. The script has already written `TRADE-LOG.md` and marked the signal as executed.
