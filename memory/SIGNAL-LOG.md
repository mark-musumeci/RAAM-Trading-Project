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

## Signal 2026-10 (as of 2026-10-30) -> allocation for 2026-11

| # | ETF | Mom % | Vol % | Avg corr | Trend | rM | rV | rC | Score | Weight |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **SCHP** | -0.77 | 4.44 | 0.245 | -2 | 4 | 1 | 4 | 3.001 | 0% |
| 2 | **DBC** | 26.50 | 15.13 | -0.315 | -2 | 1 | 10 | 1 | 3.973 | 20% |
| 3 | **AGG** | -1.25 | 4.91 | 0.355 | -2 | 6 | 2 | 6 | 4.668 | 0% |
| 4 | **VV** | 1.74 | 10.50 | 0.379 | -2 | 3 | 4 | 8 | 4.999 | 20% |
| 5 | **BTC** | 24.80 | 31.35 | 0.229 | -2 | 2 | 12 | 3 | 5.642 | 20% |
| 6 | IGOV | -2.00 | 6.47 | 0.429 | -2 | 8 | 3 | 9 | 6.669 | 0% |
| 7 | VAW | -1.38 | 13.37 | 0.375 | -2 | 7 | 8 | 7 | 7.335 | 0% |
| 8 | EFA | -0.96 | 11.12 | 0.464 | -2 | 5 | 5 | 12 | 7.335 | 0% |
| 9 | RWR | -4.99 | 14.17 | 0.148 | -2 | 11 | 9 | 2 | 7.338 | 0% |
| 10 | IJH | -3.33 | 12.04 | 0.442 | -2 | 9 | 6 | 11 | 8.670 | 0% |
| 11 | IJR | -3.88 | 12.20 | 0.441 | -2 | 10 | 7 | 10 | 9.004 | 0% |
| 12 | EEM | -7.09 | 21.16 | 0.307 | -2 | 12 | 11 | 5 | 9.340 | 0% |

**Momentum hurdle:** 1.21% (SGOV 4-month momentum); selected ETFs at or below it gave their slot to SGOV.

**Cap:** BTC capped at 5% of the portfolio (uncapped 10%); 5% moved to cash.

**Shield (RAAM, 50% of portfolio):** VV 20%, DBC 20%, BTC 20%, SGOV 40%
**Core:** QQQM 50%  ·  trend filter QQQM month-end 284.34 vs 10-month average 278.85 → **ON: held**

**Core & Shield target allocation:** VV 10%, DBC 10%, BTC 5%, SGOV 25%, QQQM 50%

**Context:** Versus the 2026-09 signal, this is the first month on the new Core & Shield rules, so everything is new: QQQM 50% (trend ON), VV, DBC and BTC, and SGOV 25%. SPY, BIL, IBIT and AGG are exits; the sell-only symbols are sold at the 2 Nov rebalance. DBC (momentum +26.5%, correlation -0.31) and BTC (momentum +24.8%) drove their selections; VV rode momentum +1.7%. SCHP and AGG were selected but their momentum is below the 1.21% SGOV hurdle, so their slots went to SGOV, and BTC's 10% was capped to 5%.
Macro: October saw 10Y Treasury yields around 5.15-5.27%, oil volatile near $88-100, equities up while REITs lagged on yields.
