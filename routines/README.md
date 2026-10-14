# Claude Code routine prompts

Each `.md` file here is **only the prompt**. Copy the whole file into the routine's instructions box. Create routines at **claude.ai/code/routines → New routine**, or with `/schedule` in the Claude Code CLI.

| Prompt file | Routine name | Schedule (US/Eastern) | What it does |
|---|---|---|---|
| [morning.md](morning.md) | RAAM – Morning | Weekdays 09:45 | Rebalance on the first trading day of the month, or when the circuit breaker is tripped. Otherwise it does nothing. |
| [close.md](close.md) | RAAM – Close | Weekdays 16:30 | Daily health check, the month-end signal (last trading day), and the monthly review (first trading day). |
| [report.md](report.md) | RAAM – Monthly Report | Days 28–31, 19:00 EDT / 18:00 EST | On the last trading day only: builds a one-page PDF report (Core & Shield vs 60/40), commits it to `reports/` and posts it to Discord. Otherwise it does nothing. |

## Cron schedules (stored in UTC)
The routine API stores crons in **UTC**, and they do **not** shift with daylight saving. These values are chosen so that both routines land safely in both seasons:

| Routine | Cron (UTC) | Summer (EDT) | Winter (EST) | Why it's safe |
|---|---|---|---|---|
| RAAM – Morning | `45 14 * * 1-5` | 10:45 | 09:45 | always after the 09:30 open |
| RAAM – Close | `30 21 * * 1-5` | 17:30 | 16:30 | always after the 16:00 close |
| RAAM – Monthly Report | `0 23 28-31 * *` | 19:00 | 18:00 | after the Close routine has saved the new signal; at most 4 quick runs a month |

Runs may start a few minutes late because of scheduling stagger. Holidays need no special handling: the scripts check Alpaca's market calendar and do nothing on market holidays.

## Repository must be attached
Each routine must have `musu-codes/RAAM-Trading-Project` selected under **Repositories**. Without it, the run starts in an empty container and stops with "no repository present". The Claude GitHub app, or `/web-setup`, must have access to this private repo.

## Settings for all routines
| Setting | Value |
|---|---|
| Repository | `musu-codes/RAAM-Trading-Project` |
| Environment | your RAAM cloud environment (see below) |
| Connectors | remove all; none are needed |
| Model | default |

## Cloud environment (set this up first)
- **Environment variables:** paste in everything from `env.template` with real values. This is the only place routines get API keys from. Don't use "API credentials".
- **Network access:** Custom. Allow `paper-api.alpaca.markets`, `data.alpaca.markets` and `discord.com`, and tick "include default package managers".
- **Setup script:** `pip install -r requirements.txt`

## First runs
1. On each routine, click **Run now** with the text `dry_run`.
2. Read the transcript. A green status only means it didn't crash. Check for:
   - missing env var errors;
   - `host_not_allowed` network errors;
   - whether the push to `main` worked.

To test the month-end path mid-month, use **Run now** on *RAAM – Close* with `dry_run force_date=2026-08-31`.

To test the report, use **Run now** on *RAAM – Monthly Report* with `force`. It builds and posts a report for the current month to date. There's no dry-run mode, because it never trades.
