---
description: Monthly Core & Shield review vs 60/40 (headline), 30/70, SPY and equal-weight 7Twelve
argument-hint: "[month=YYYY-MM] [force]"
---
Monthly review (runs on the first trading day of the month, after the close). Follow the SOP in CLAUDE.md.

1. Run `python3 scripts/raam.py review`.
   - If `$ARGUMENTS` has `month=YYYY-MM`, pass `--month YYYY-MM`.
   - If it has `force`, pass `--force`.
   - `noop` → stop quietly.
2. Prepend a section to `memory/MONTHLY-REVIEW.md`, below the header:
   - `## <month>`
   - A table of Core & Shield return % (`portfolio_return_pct`), **60/40 %** (the headline benchmark), 30/70 %, SPY % and equal-weight 7Twelve %, plus Core & Shield minus each.
   - The split between the halves: Core return (`core_return_est_pct`) and Shield (RAAM) return (`shield_return_est_pct`). These are estimates from the target weights.
   - The allocation held that month, with each held ETF's return.
   - The best and worst contributors.
   - Two or three observations. Is the model behaving as designed? Did any factor dominate? Was any cash (BIL) substitution triggered, and what was the cash-momentum hurdle?
   - **Versus history:** compare the month's return, cash (BIL) weight and drawdown with the "Normal ranges" in `memory/BACKTEST-SUMMARY.md`. Say whether each is normal or unusual.
   - **Hypotheses:** if the month is evidence for or against one of the "Findings" in BACKTEST-SUMMARY.md, note it in one line (e.g. "trend filter excluded VV, which rose 4% — supports finding 2"). These accumulate evidence for the owner's 6- and 12-month reviews. Never act on them.
   - **Scorecard against `memory/EVALUATION-PLAN.md`:** one line per criterion (O1–O8 every month; B1–B5 from the 3rd month on), each marked PASS / FAIL / n/a with the number.
     - Slippage (O6) comes from the executed signal's `fills` (`slippage_bps`) and the TRADE-LOG.
     - Operations evidence (O1–O5) comes from the git log and RESEARCH-LOG.
     - Never change the criteria. If one can't be measured, write n/a with the reason.
   - Include "Open questions" only if something relates to the ambiguities A1–A7 in TRADING-STRATEGY.md.
   - Plain facts. No strategy changes.
3. **Shadow variants:** run `python3 scripts/shadow.py`. On the first trading day it closes last month's shadow returns and refreshes `memory/SHADOW-LOG.md`.
   - Add a short **"Shadow variants"** part to the review section:
     - last month's return for each variant and 60/40, plus since start;
     - the gap *Live account − Live model*, as evidence for B4 (replication).
   - Plain facts only. Never recommend switching variants; that is the owner's decision at a checkpoint.
   - If the script errors, write "shadow: <reason>" and carry on.
4. Update the milestone checkboxes in `memory/PROJECT-STATUS.md` if any were reached.
5. Discord: `RAAM <month> review: Core & Shield X% vs 60/40 Y% (Core A%, Shield B%) | best <ETF>, worst <ETF> | scorecard <n> pass / <m> fail`.
