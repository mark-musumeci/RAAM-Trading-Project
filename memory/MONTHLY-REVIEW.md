# Monthly Review

One section per month, newest first. Written by `/monthly-review` from `scripts/raam.py review`.
Compares RAAM (paper account) against SPY and the equal-weight 7Twelve portfolio.

## 2026-09
Pre-inception month: the account held cash only (first rebalance executed 2026-10-01), so Core & Shield was 0.00% and no comparison is meaningful.

| Portfolio | Return % | Core & Shield minus it |
|---|---|---|
| Core & Shield (cash, not invested) | 0.00 | n/a |
| 60/40 (headline) | -1.24 | n/a (not invested) |
| 30/70 | -1.92 | n/a |
| SPY | -0.33 | n/a |
| Equal-weight 7Twelve | -2.04 | n/a |

- **Core vs Shield:** Core est. -1.24%; Shield est. n/a (not invested).
- **Allocation held:** none (cash). Targets from the 2026-09 signal, executed 2026-10-01: SPY 30, AGG 20, BIL 35, DBC 10, IBIT 5.
- **ETF returns (Sep):** best IBIT +5.98%, DBC +3.26%, BIL +0.29%; worst VAW -7.39%, IJR -5.53%, RWR -5.49%. Targets chose DBC and IBIT (the two best) with BIL 35%.
- **Observations:** broad weakness (equities and bonds both down; AGG -2.6%), a pattern where cash and commodities lead. The model went defensive (BIL 35%, within the 50% max) as designed. IBIT was picked and hit the 5% cap.
- **Versus history:** return n/a; BIL 35% is above the 16% average but below the 50% max (normal for a weak market); drawdown 0.0% (normal).
- **Hypotheses:** none; no invested month to evaluate.
- **Scorecard (O1-O8):**
  - O1 PASS: signal saved 2026-09-30, research logged first.
  - O2 PASS: 5 of 5 orders filled on 2026-10-01.
  - O3 PASS: daily health runs pushed to main.
  - O4 PASS: 0 unexplained halts.
  - O5 PASS: report posted 2026-09-30 (git log: report commit).
  - O6 PASS: value-weighted avg |slippage| ~1.7 bps; max single order 10.5 bps (IBIT).
  - O7 PASS: all holdings within 0.27 pp of target after the rebalance.
  - O8 PASS: IBIT 5.00%.
  - B1-B5: n/a (start from the 3rd month).
