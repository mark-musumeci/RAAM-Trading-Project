---
description: Month-end one-page PDF performance report (Core & Shield vs 60/40), posted to Discord
argument-hint: "[force] [force_date=YYYY-MM-DD] [month=YYYY-MM]"
---
Monthly report. Follow the SOP in CLAUDE.md. This is reporting only: no orders, and no changes to config or rules.

1. Build the flags from `$ARGUMENTS`: `force` → `--force`; `force_date=D` → `--date D`; `month=YYYY-MM` → `--month YYYY-MM`.
2. Run `python3 scripts/report.py --metrics-only <flags>`.
   - `noop` means it isn't the last trading day of the month. Reply "report: not month-end" and stop. No commit, no Discord message.
   - `halt` or `error`: send `RAAM ⚠️ monthly report failed: <reason>` to Discord and stop.
3. Write exactly **3 short factual bullets** to `reports/<month>-notes.txt`, one per line, starting with "- ". Base them **only** on the metrics JSON:
   - what drove the month: the biggest contributors from `holdings`, and the Core vs Shield behaviour;
   - how Core & Shield compared with 60/40, and, if 60/40 fell, what share of the loss it took;
   - whether anything is outside the backtest's normal ranges (`checks`), or "all checks within normal ranges".

   No advice, no forecasts, no strategy suggestions, and no numbers that aren't in the JSON. Keep each bullet under about 30 words.
4. Run `python3 scripts/report.py <flags> --notes-file reports/<month>-notes.txt`. It writes `reports/<month>.pdf`. Confirm `status` is `ok` and the file exists.
5. Commit `reports/` with the message `report: <month> C&S <X>% vs 60/40 <Y>%`, then push, following the SOP.
6. Discord, in one message with the PDF attached:
   `bash scripts/discord.sh --file reports/<month>.pdf "RAAM <Month YYYY> report | C&S <X>% vs 60/40 <Y>% | since inception <Z>% | <checks summary>"`
