# 24/7 RAAM Trading Bot

An autonomous implementation of the **Ranked Asset Allocation Model**, from Gioele Giordano's 2018 Charles H. Dow Award paper:
- It trades the 12-ETF 7Twelve universe on an **Alpaca paper account**.
- It is run by **Claude Code cloud routines**.
- This repo is the bot's persistent disk: code, config and memory. Each routine run clones it, acts, and pushes its memory back.

Each month the bot ranks 11 ETFs on momentum, volatility and correlation, adjusts for an ATR trend filter, and holds the top 5 at 20% each. Any of those 5 whose momentum does not beat cash's own momentum is swapped for BIL (T-bills). It rebalances once a month and holds; there are no stops. The full rules and open questions are in [memory/TRADING-STRATEGY.md](memory/TRADING-STRATEGY.md).

## Layout
| Path | Purpose |
|---|---|
| `CLAUDE.md` | Always-loaded operating instructions for the agent |
| `config/raam.json` | Model parameters and guardrail thresholds |
| `scripts/raam.py` | Deterministic engine: calendar, signal, rebalance, health, review |
| `scripts/alpaca.sh` | Thin curl wrapper for Alpaca (ad-hoc and manual use) |
| `scripts/discord.sh` | Discord notifications via channel webhook (`DISCORD_WEBHOOK_URL`) |
| `.claude/commands/` | `/health` `/signal` `/rebalance` `/monthly-review` `/research` `/portfolio` `/trade` |
| `memory/` | Strategy, logs, signals (`signals/*.json`) and `state.json` (high-water mark, circuit breaker) |
| `tests/` | pytest unit tests for the indicators, ranking and order planning |

## Schedule (Mon–Fri; cron is UTC, see routines/README.md)
| Routine | Time | Runs |
|---|---|---|
| **RAAM – Morning** | 09:45 EST / 10:45 EDT | `/rebalance`. It acts only on the first trading day of the month, or when the circuit breaker is tripped. |
| **RAAM – Close** | 16:30 EST / 17:30 EDT | `/health` every day. Then `/signal` on the last trading day of the month, and `/monthly-review` on the first trading day. |

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
