# Claude Code routine prompts

Each `.md` file here is **only the prompt**. Copy the whole file into the routine's instructions box. Create routines at **claude.ai/code/routines → New routine**, or with `/schedule` in the Claude Code CLI.

| Prompt file | Routine name | Schedule (US/Eastern) | What it does |
|---|---|---|---|
| [morning.md](morning.md) | RAAM – Morning | Weekdays 09:45 | Rebalance on the first trading day of the month, or when the circuit breaker is tripped. Otherwise it does nothing. |
| [close.md](close.md) | RAAM – Close | Weekdays 16:30 | Daily health check, the month-end signal (last trading day), and the monthly review (first trading day). |

## Settings for both routines
| Setting | Value |
|---|---|
| Repository | `musu-codes/24.7-RAAM-Trading` |
| Environment | your RAAM cloud environment (see below) |
| Connectors | remove all; none are needed |
| Model | default |

## Cloud environment (set this up first)
- **Environment variables:** paste in everything from `env.template` with real values. This is the only place routines get API keys from. Don't use "API credentials".
- **Network access:** Custom. Allow `paper-api.alpaca.markets`, `data.alpaca.markets`, `api.perplexity.ai` and `api.callmebot.com`, and tick "include default package managers".
- **Setup script:** `pip install -r requirements.txt`

## Timezone note
Schedule times are entered in **your local time**. Use your local equivalent of 09:45 and 16:30 ET.
- If you are outside the US, re-check the offset around daylight-saving changes.
- A Morning run that fires before the 09:30 ET open stops with "market is closed" and places no orders, so it fails safe. On a rebalance day, you would then need to click **Run now** once the market is open.

## First runs
1. On each routine, click **Run now** with the text `dry_run`.
2. Read the transcript. A green status only means it didn't crash. Check for:
   - missing env var errors;
   - `host_not_allowed` network errors;
   - whether the push to `main` worked.

To test the month-end path mid-month, use **Run now** on *RAAM – Close* with `dry_run force_date=2026-08-31`.
