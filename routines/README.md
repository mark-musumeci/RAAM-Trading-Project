# Claude Code routine prompts

Paste-ready configurations for the two cloud routines. Create them at **claude.ai/code/routines → New routine**, or with `/schedule` in the Claude Code CLI.

| File | Routine | When (US/Eastern) |
|---|---|---|
| [morning.md](morning.md) | RAAM – Morning | Weekdays 09:45: rebalance on the first trading day, or when the circuit breaker is tripped |
| [close.md](close.md) | RAAM – Close | Weekdays 16:30: daily health, the month-end signal, and the monthly review |

## Before creating them
Set up the cloud environment first (see the main README):
- Environment variables from `env.template`.
- Custom network access.
- Setup script `pip install -r requirements.txt`.

## Timezone note
Schedule times are entered in **your local time**. Use your local equivalent of 09:45 and 16:30 ET.
- If you are outside the US, the gap to ET changes for a week or two around daylight-saving switches, so re-check it then.
- A Morning run that fires before the 09:30 ET open stops with "market is closed" and places no orders, so it fails safe. On a rebalance day, you would then need to click **Run now** once the market is open.

## First runs
1. On each routine, click **Run now** with the text `dry_run`.
2. Open the run and read the transcript. A green status only means it didn't crash. Check for:
   - missing env var errors;
   - `host_not_allowed` network errors;
   - whether the push to `main` worked.
3. Then let the schedules run.

## Testing the month-end path mid-month
Use **Run now** on *RAAM – Close* with the text `dry_run force_date=<last trading day of last month>`.
