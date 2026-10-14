# RAAM Trading Bot Project — Core & Shield

An autonomous **Core & Shield** portfolio on an **Alpaca paper account**, run by **Claude Code cloud routines**:
- **Core, 50%:** a fixed 60/40, 30% SPY + 20% AGG, reset monthly. It does the growing.
- **Shield, 50%:** the **Ranked Asset Allocation Model**, from Gioele Giordano's 2018 Charles H. Dow Award paper. It does the defending.
  - Each month it ranks 12 candidates (11 of the 7Twelve ETFs plus IBIT, a spot-Bitcoin ETF) on momentum, volatility and correlation, and holds the top 5.
  - IBIT is capped at 5% of the whole portfolio.
  - Any pick whose momentum doesn't beat cash is swapped for BIL (T-bills).

It rebalances once a month and holds; there are no stops. This repo is the bot's persistent disk: code, config and memory. Each routine run clones it, acts, and pushes its memory back.

Backtest, 2009–2026: 7.5%/yr at a Sharpe of about 1.1, the same as 60/40, but with about 40% smaller drawdowns. 2022 was −7.8% vs 60/40's −15.2%. The rules are in [memory/TRADING-STRATEGY.md](memory/TRADING-STRATEGY.md) and the evidence is in [memory/BACKTEST-SUMMARY.md](memory/BACKTEST-SUMMARY.md).

## Layout
| Path | Purpose |
|---|---|
| `CLAUDE.md` | Always-loaded operating instructions for the agent |
| `config/raam.json` | Model parameters and guardrail thresholds |
| `scripts/raam.py` | Deterministic engine: calendar, signal, rebalance, health, review |
| `scripts/alpaca.sh` | Thin curl wrapper for Alpaca (ad-hoc and manual use) |
| `scripts/discord.sh` | Discord notifications via channel webhook (`DISCORD_WEBHOOK_URL`), with optional file attachment (`--file`) |
| `scripts/report.py` | One-page monthly PDF report: Core & Shield vs 60/40, holdings, next allocation, backtest checks |
| `reports/` | Archive of the monthly PDF reports and their commentary notes |
| `.claude/commands/` | `/health` `/signal` `/rebalance` `/monthly-review` `/report` `/research` `/portfolio` `/trade` |
| `memory/` | Strategy, logs, signals (`signals/*.json`) and `state.json` (high-water mark, circuit breaker) |
| `tests/` | pytest unit tests for the indicators, ranking, order planning, commands and report |

## Schedule (cron is UTC, see routines/README.md)
| Routine | Time | Runs |
|---|---|---|
| **RAAM – Morning** | 09:45 EST / 10:45 EDT | `/rebalance` (Core and Shield together). It acts only on the first trading day of the month, or when the circuit breaker is tripped. |
| **RAAM – Close** | 16:30 EST / 17:30 EDT | `/health` every day. Then `/signal` on the last trading day of the month, and `/monthly-review` on the first trading day. |
| **RAAM – Monthly Report** | 18:00 EST / 19:00 EDT, days 28–31 | `/report` on the last trading day of the month only: a one-page PDF posted to Discord. |

## Local quickstart
```bash
pip install -r requirements.txt
cp env.template .env          # fill in Alpaca paper keys etc.
python -m pytest -q            # unit tests, no network
python scripts/raam.py calendar
python scripts/raam.py health --dry-run
python scripts/raam.py signal --force --dry-run     # compute today's ranks without saving
python scripts/raam.py rebalance --force --dry-run  # show the orders it would place
bash scripts/discord.sh "RAAM test"
```

## Cloud routine setup
1. **Cloud environment.** Set this up at claude.ai/code, in the environment settings:
   - **Environment variables:** paste in everything from `env.template` with real values, in the same `KEY=value` format. Keep `PAPER_TRADING=true`.
     - This is the **only** place routines get keys from; the scripts never read a `.env` file in the cloud.
     - Do not use the "API credentials" section. Those keys are injected by a proxy and are never visible to the scripts.
   - **Network access:** Custom. Allow `paper-api.alpaca.markets`, `data.alpaca.markets` and `discord.com`, and tick "include default package managers".
   - **Setup script:** `pip install -r requirements.txt`
2. **Routines.** Create them with `/schedule` or at claude.ai/code/routines:
   - repo `musu-codes/24.7-RAAM-Trading`;
   - the environment above;
   - connectors: none.

   The paste-ready prompts and settings are in [routines/](routines/):
   - [routines/morning.md](routines/morning.md) runs weekdays at 09:45 ET.
   - [routines/close.md](routines/close.md) runs weekdays at 16:30 ET.
3. **First runs.** Click **Run now** with the text `dry_run` and read the transcript. A green status only means the run didn't crash.

## Safety
- Paper only, unless both `PAPER_TRADING=false` and `LIVE_CONFIRM=yes` are set.
- A circuit breaker (−20% from peak, or −5% in one day) moves the portfolio to 100% BIL; it re-enters automatically at the next monthly rebalance with the fresh signal.
- Research never changes the allocation. Claude may halt and alert, but never improvises trades.
