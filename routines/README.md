# Claude Code routine prompts

Each `.md` file here is **only the prompt**. Copy the whole file into the routine's instructions box. Create routines at **claude.ai/code/routines → New routine**, or with `/schedule` in the Claude Code CLI.

| Prompt file | Routine name | Schedule (US/Eastern) | What it does |
|---|---|---|---|
| [morning.md](morning.md) | RAAM – Morning | Weekdays 09:45 | Rebalance on the first trading day of the month, or when the circuit breaker is tripped. Otherwise it does nothing. |
| [close.md](close.md) | RAAM – Close | Weekdays 16:30 | Daily health check, the month-end signal (last trading day), and the monthly review (first trading day). |

## Cron schedules (US/Eastern, which is also your local time)
| Routine | Cron | Meaning |
|---|---|---|
| RAAM – Morning | `45 9 * * 1-5` | 09:45, Monday–Friday |
| RAAM – Close | `30 16 * * 1-5` | 16:30, Monday–Friday |

There are two ways to set these:
- **Web form:** pick the **Weekdays** preset and enter the time.
- **CLI:** run `/schedule update` and give it the cron expression.

Schedule times are in your local time zone. Your PC is on US Eastern, so no conversion is needed, and daylight-saving changes are handled automatically. Runs may start a few minutes late because of scheduling stagger. Holidays need no special handling: the scripts check Alpaca's market calendar and do nothing on market holidays.

## Settings for both routines
| Setting | Value |
|---|---|
| Repository | `musu-codes/24.7-RAAM-Trading` |
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
