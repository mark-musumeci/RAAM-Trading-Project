# Monthly Review

One section per month, newest first. Written by `/monthly-review` from `scripts/raam.py review`.
Compares RAAM (paper account) against SPY and the equal-weight 7Twelve portfolio.

## 2026-10
First invested month, run under the previous design (fixed 60/40 Core; SPY 30, AGG 20, BIL 35, DBC 10, IBIT 5). Counts toward O1-O8 only (checkpoint 0); the 12-month evaluation of the new Core starts at the 2026-11-02 rebalance.

| Portfolio | Return % | Core & Shield minus it |
|---|---|---|
| Core & Shield (account, `review`) | 1.03 | n/a |
| 60/40 (headline) | 0.37 | +0.65 |
| 30/70 | 1.33 | -0.31 |
| SPY | -0.91 | +1.93 |
| Equal-weight 7Twelve | 0.44 | +0.58 |

- **Data caveat:** the review's 1.03% uses Alpaca portfolio history ($100,000.00 -> $101,024.89), but the 2026-10-30 health run recorded equity of $100,300.91, and the weights x ETF returns below sum to only about +0.29%. The shadow log's "Live account" for Oct is +0.27%. The first number is probably distorted by the history endpoint (start-of-month cash baseline / end-of-day point). Treat it as unreconciled; not acted on. The PDF report said C&S +0.3% vs 60/40 +0.4%.
- **Core vs Shield (estimates from targets):** Core (60/40 sleeve) +0.37%; Shield -0.67%.
- **Allocation held and ETF returns:** SPY 30% (-0.91%), AGG 20% (+2.29%), BIL 35% (+0.35%), DBC 10% (+3.99%), IBIT 5% (-8.41%).
- **Contributors (weight x return):** best AGG +0.46 pp, DBC +0.40 pp; worst IBIT -0.42 pp, SPY -0.27 pp.
- **Observations:** the defensive tilt worked as designed (BIL 35%, AGG and DBC up while SPY and IBIT fell). IBIT's drop (-8.4%) cost about 0.42 pp, so the 5% cap limited that loss. QQQM, the incoming Core, fell -6.66% in October and EEM -8.61%. No cash-substitution anomaly noted.
- **Versus history (previous-design norms):** return within the normal -3%..+3% band; BIL 35% above the 16% average but within the 50% max; drawdown about -0.8% at month-end, normal.
- **Hypotheses:** none strong. A single month is noise.
- **Scorecard (O1-O8, previous Core):**
  - O1 PASS: signal 2026-09-30 saved, research logged first (2026-10-30 signal and research also done).
  - O2 PASS: 5 of 5 orders filled on 2026-10-01.
  - O3 PASS: daily health runs pushed to main every trading day in the month.
  - O4 PASS: 0 unexplained halts in October.
  - O5 PASS: report posted 2026-10-30 (commit `4bee3db`).
  - O6 PASS: Oct-1 slippage: avg ~1.7 bps, max single 10.5 bps (IBIT).
  - O7 PASS: all holdings within 0.27 pp of target after the 10-01 rebalance.
  - O8 PASS: IBIT 5.00% at the rebalance.
  - B1-B5: n/a (start from the 3rd month).
- **November pre-note (belongs to the 11-02 rebalance; scored in the December review):** the first attempt halted with an AGG sell rejected (403 insufficient qty, 0 fills). A fix (exact fractional exit) was committed and an owner-sanctioned retry filled 9 of 9 orders. Fills had avg slippage -3.2 bps and max single |20.5| bps (BTC buy, a favourable fill). This is a candidate O4/O6 discussion for December.

**Shadow variants (Oct, to 2026-11-02):** Live model +0.20%, No Bitcoin +0.45%, Core 50% SPY -0.48%, Core 40/10 -0.14%, Bitcoin satellite +0.08%, 60/40 +0.66%; Live account +0.27%. Live account minus Live model: +0.07 pp (B4 evidence). Since start: Live model -1.17%, 60/40 +0.06%, Live account -0.84%. Facts only.

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
