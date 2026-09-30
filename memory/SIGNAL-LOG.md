# Signal Log

One section per month-end signal, written by `scripts/raam.py signal`. Bold = selected.
The machine-readable version (with executed fills) is `memory/signals/YYYY-MM.json`.

## Signal 2026-09 (as of 2026-09-30) -> allocation for 2026-10

| # | ETF | Mom % | Vol % | Avg corr | Trend | rM | rV | rC | Score | Weight |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **RWR** | -0.76 | 10.81 | 0.064 | -2 | 5 | 5 | 2 | 4.001 | 0% |
| 2 | **DBC** | 7.77 | 19.96 | -0.252 | -2 | 2 | 10 | 1 | 4.325 | 20% |
| 3 | **TIP** | -3.77 | 4.65 | 0.385 | -2 | 9 | 1 | 4 | 4.670 | 0% |
| 4 | **IBIT** | 16.92 | 44.23 | 0.231 | -2 | 1 | 12 | 3 | 5.316 | 20% |
| 5 | **AGG** | -3.21 | 5.03 | 0.440 | -2 | 8 | 2 | 7 | 5.670 | 0% |
| 6 | VV | 1.27 | 10.92 | 0.473 | -2 | 3 | 6 | 9 | 5.999 | 0% |
| 7 | IJR | -1.09 | 10.77 | 0.467 | -2 | 6 | 4 | 8 | 6.001 | 0% |
| 8 | EFA | 1.05 | 12.70 | 0.521 | -2 | 4 | 8 | 12 | 7.999 | 0% |
| 9 | IGOV | -4.79 | 7.47 | 0.482 | -2 | 11 | 3 | 10 | 8.005 | 0% |
| 10 | IJH | -2.94 | 11.05 | 0.491 | -2 | 7 | 7 | 11 | 8.336 | 0% |
| 11 | VAW | -5.09 | 16.44 | 0.417 | -2 | 12 | 9 | 5 | 8.671 | 0% |
| 12 | EEM | -4.20 | 22.74 | 0.420 | -2 | 10 | 11 | 6 | 9.004 | 0% |

**Momentum hurdle:** 1.17% (BIL 4-month momentum); selected ETFs at or below it gave their slot to BIL.

**Cap:** IBIT capped at 5% of the portfolio (uncapped 10%); 5% moved to cash.

**Shield (RAAM, 50% of portfolio):** DBC 20%, IBIT 20%, BIL 60%
**Core (fixed):** SPY 30%, AGG 20%

**Core & Shield target allocation:** DBC 10%, AGG 20%, IBIT 5%, BIL 35%, SPY 30%

**Context:** First live-paper signal, so all Shield slots are new entries (no prior holdings). Drivers: DBC ranks best on correlation (-0.25) and 2nd on momentum (+7.8%); IBIT ranks 1st on momentum (+16.9%) but last on volatility (44%), selected on overall score; its 10% Shield-slice weight is capped to 5% and the excess goes to BIL. RWR, TIP and AGG were selected but their momentum is at or below the 1.17% BIL hurdle, so their slots went to BIL (60% of Shield).
Macro: September saw a Treasury yield surge (10Y highest since 2007, 30Y 5.6%), REITs/materials about -7% and gold weakening, while tech and Bitcoin held up.
