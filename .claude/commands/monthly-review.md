---
description: Monthly performance review vs SPY and equal-weight 7Twelve
argument-hint: "[month=YYYY-MM] [force]"
---
Monthly review (runs on the first trading day of the month, after the close). Follow the SOP in CLAUDE.md.

1. Run `python3 scripts/raam.py review`.
   - If `$ARGUMENTS` has `month=YYYY-MM`, pass `--month YYYY-MM`.
   - If it has `force`, pass `--force`.
   - `noop` → stop quietly.
2. Prepend a section to `memory/MONTHLY-REVIEW.md`, below the header:
   - `## <month>`
   - A table of RAAM return %, SPY %, equal-weight 7Twelve %, and the RAAM minus each benchmark.
   - The allocation held that month, with each held ETF's return.
   - The best and worst contributors.
   - Two or three observations. Is the model behaving as designed? Did any factor dominate? Was any cash (BIL) substitution triggered, and what was the cash-momentum hurdle?
   - **Versus history:** compare the month's return, cash (BIL) weight and drawdown with the "Normal ranges" in `memory/BACKTEST-SUMMARY.md`. Say whether each is normal or unusual.
   - **Hypotheses:** if the month is evidence for or against one of the "Findings" in BACKTEST-SUMMARY.md, note it in one line (e.g. "trend filter excluded VV, which rose 4% — supports finding 2"). These accumulate evidence for the owner's 6- and 12-month reviews. Never act on them.
   - Include "Open questions" only if something relates to the ambiguities A1–A7 in TRADING-STRATEGY.md.
   - Plain facts. No strategy changes.
3. Update the milestone checkboxes in `memory/PROJECT-STATUS.md` if any were reached.
4. Discord: `RAAM <month> review: RAAM X% vs SPY Y% vs 7Twelve Z% | best <ETF>, worst <ETF>`.
