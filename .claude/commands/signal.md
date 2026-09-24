---
description: Month-end Core & Shield signal — RAAM factors and ranks for the Shield, plus the fixed Core, giving next month's targets
argument-hint: "[dry_run] [force] [force_date=YYYY-MM-DD]"
---
Month-end signal. Follow the SOP in CLAUDE.md.

1. Run `python3 scripts/raam.py calendar`. If today is **not** the last trading day of the month and `$ARGUMENTS` has no `force`/`force_date`, reply "signal: not month-end" and stop. Send no Discord message for this part.
2. Run `/research` with its default month-end scan. It covers all 12 ETFs plus the macro backdrop.
   - If research reports a **structural** problem with any universe ETF (closure, merger, delisting, ticker or index change, trading halt), **do not generate the signal**. Send a Discord ⚠️ message explaining it and stop.
3. Run `python3 scripts/raam.py signal`. Add `--dry-run`, `--force` and `--date` as the arguments request.
4. Check the output:
   - `status` is `ok`;
   - 11 rows, 5 selected;
   - `shield_targets` (RAAM) sum to 100%, and every non-zero Shield weight is 20%, or a multiple of 20% for BIL;
   - `targets` (the whole portfolio) sum to 100%;
   - each target equals the Core weight plus 0.5 × its Shield weight. In particular SPY is at least 30% and AGG at least 20%.

   If anything fails, send ⚠️ and stop.
5. In `memory/SIGNAL-LOG.md`, under the section the script just wrote, add a 2–4 line **"Context"** note:
   - what changed vs last month (entries and exits);
   - which factor drove each change;
   - one line of macro backdrop from the research.

   The script writes the table; you only add the note. The **Trend** column is informational only (`w_trend` = 0). Never describe it as driving a selection.
6. Discord: `RAAM signal <month> → <effective month> | Shield: VV, EFA, RWR + BIL 40% | Portfolio: SPY 30%, AGG 20%, VV 10%, ... | changes: +X -Y | executes next trading day ~09:45–10:45 ET`.
