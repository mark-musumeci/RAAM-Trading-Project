# Evaluation Plan: Core & Shield paper trading

**Written 2026-09-26, before the first trade (2026-10-01).** These criteria are fixed in advance so the results can't move the goalposts. Change this file only with an owner decision, noted in the change log at the bottom, and never because of results already seen.

**Benchmark:** 60/40 (60% SPY + 40% AGG). **Not SPY:** trailing SPY in rising markets is expected by design.
**Source numbers:** the paper account (the monthly PDF report, `scripts/raam.py review`, `memory/TRADE-LOG.md`) and the backtest norms in `memory/BACKTEST-SUMMARY.md`.

## 1. Operations: does it run correctly? (checked every month)
| # | Criterion | Pass |
|---|---|---|
| O1 | The month-end signal is saved on the last trading day, and research runs before it | every month |
| O2 | The rebalance runs on the first trading day, and every order has status `filled` | every month |
| O3 | Daily health runs succeed and push to `main` | ≥ 95% of trading days |
| O4 | No unexplained halts. A halt with a clear, correct reason, like a closed market, counts as working. | 0 unexplained |
| O5 | The monthly PDF report arrives in Discord on the last trading day | every month |
| O6 | **Execution cost:** value-weighted average slippage per rebalance | ≤ 10 bps, and no single order > 30 bps |
| O7 | After a rebalance, every holding is within ±2 percentage points of its target | every rebalance |
| O8 | IBIT never exceeds 5% of the portfolio at a rebalance | every rebalance |

## 2. Behaviour: does it act like the backtest? (from 3 months)
| # | Criterion | Pass |
|---|---|---|
| B1 | Monthly return is within the backtest's extreme range, −5.7% to +6.9% | every month (outside = investigate) |
| B2 | Cash (BIL) is at most 50% of the portfolio | every month |
| B3 | Drawdown since inception stays above the backtest's worst, −14.1% (−14.6% without IBIT) | always |
| B4 | **Replication:** the same months run through `backtest/backtest.py` give returns close to the live account's | average absolute gap ≤ 0.3 pp per month |
| B5 | In months when 60/40 falls, Core & Shield loses ≤ 65% as much (the backtest norm, 63%). Some months will miss, so pass/fail is judged on the average across down months. | average ≤ 85% (allows for noise) |

## 3. Checkpoints
| Checkpoint | Date | Question | Pass when |
|---|---|---|---|
| **1 month** | early Nov 2026 | Does it run? | O1–O8 all pass for October |
| **3 months** | early Jan 2027 | Is it reliable? | O1–O8 pass in 3 of 3 months; B1–B3 hold |
| **6 months** | early Apr 2027 | Does it behave as designed? | B1–B4 pass; B5 assessed if there were at least 2 down months for 60/40 |
| **12 months** | early Oct 2027 | Is it worth running? | See the verdict rules below |

## 4. Twelve-month verdict (decided by these rules, not by feel)
- **Working as designed** requires all of:
  - operations pass (O-criteria in ≥ 11 of 12 months);
  - B1–B4 pass;
  - the max drawdown over the 12 months is **smaller than 60/40's** over the same period;
  - if 60/40 had at least 2 down months: B5 passes.
- **Inconclusive (no test of defence)** covers everything above except that 60/40 had fewer than 2 down months. That's normal in a calm or rising year: the strategy can't prove its defence without a downturn. Continue running.
- **Not working** if any of:
  - B4 fails, meaning the live account doesn't match the model: an implementation problem;
  - B5 fails clearly (average > 100% of 60/40's loss);
  - the drawdown is larger than 60/40's in a year when 60/40 fell.
- **Explicitly NOT a failure:** trailing SPY in any period, or trailing 60/40 in a year when 60/40 rose.

## 5. What happens after a checkpoint
- A failed **O**-criterion means an operational fix: code, routine or broker. The strategy doesn't change.
- A failed **B**-criterion means investigating first: data, implementation, or a genuine regime difference. Strategy changes are proposed only with backtest evidence and decided by the owner.
- Ideas parked for the 6-month checkpoint, tested as fixed-in-advance variants and never adopted mid-month:
  - swapping VV→TLT and VAW→GLD;
  - capped risk-based sizing;
  - staggered rebalancing.
- **Shadow variants** (from October 2026): `scripts/shadow.py` tracks the variants pre-registered in `config/shadow.json` every month without trading them, in `memory/SHADOW-LOG.md`. The variants are: no Bitcoin, Core 50% SPY, Core 40/10, and Bitcoin as a separate 5% satellite. This gives live evidence for checkpoint decisions without resetting this evaluation. The *Live model* row against the live account is extra monthly evidence for B4. The variants are judged only at checkpoints, never adopted mid-month, and never added or changed because of results already seen.
- The rating (69/100 at the start) is updated at each checkpoint using these results.

## Change log
| Date | Change | Decided by |
|---|---|---|
| 2026-09-26 | Plan written before the first trade | owner |
| 2026-09-26 | IBIT added (capped at 5%) **before the first trade**. B1/B3/B5 reference numbers updated from the 2015–2026 backtest, and O8 added. Criteria otherwise unchanged. | owner |
| 2026-10-14 | Shadow tracking of 4 pre-registered variants added (`config/shadow.json`). Evidence only: criteria and the live strategy unchanged. | owner |
