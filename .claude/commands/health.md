---
description: Daily health check — equity, drawdown, circuit breaker, drift vs targets
argument-hint: "[dry_run]"
---
Daily health check (runs every trading day after the close). Follow the SOP in CLAUDE.md.

1. Run `python3 scripts/raam.py health` (add `--dry-run` if `$ARGUMENTS` contains `dry_run`).
2. Read the JSON:
   - `alerts` non-empty → this run is a ⚠️ run. If the circuit breaker just tripped, say clearly that tomorrow's 09:45 run will move the portfolio to 100% SHY.
   - A position dropped more than 5% today, or anything else looks unusual → run a quick `/research` on that ETF, focused on today's news. Summarise the cause in one line. Do not act on it.
3. Update the "Latest health" section of `memory/PROJECT-STATUS.md`:
   - equity, day change, drawdown, high-water mark and breaker state;
   - a compact positions table (symbol, weight %, target %, drift %);
   - the timestamp.

   Replace the previous "Latest health" block; don't append.
4. Discord: one line in this format: `RAAM <date> | Equity $X (+/-Y% day) | DD Z% | <n> positions | <alerts or "all clear">`.

If `raam.py` returns `halt` or `error`, report the reason (⚠️) and stop.
