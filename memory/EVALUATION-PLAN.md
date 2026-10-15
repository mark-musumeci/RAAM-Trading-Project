# Evaluation Plan: Core & Shield paper trading

**Written 2026-09-26, before the first trade (2026-10-01). Restarted 2026-10-14** for the new Core (QQQM with a 10-month trend filter, owner decision): the 12-month evaluation now runs from the **2 Nov 2026 rebalance**. October 2026 (previous 60/40 Core) counts toward the operations criteria (O1–O8) only. Behaviour references (B1–B5) were reset from the new backtest *before* any result of the new design existed. These criteria are fixed in advance so the results can't move the goalposts. Change this file only with an owner decision, noted in the change log at the bottom, and never because of results already seen.

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
| B1 | Monthly return is within the backtest's extreme range, −8.7% to +9.1% | every month (outside = investigate) |
| B2 | Cash (BIL) matches the rules: the Core is in BIL only when the trend filter is off, and Shield cash comes only from failed picks or the IBIT cap (up to 100% when both halves are defensive) | every month |
| B3 | Drawdown since inception stays above −20%, the circuit-breaker level. Backtest worst: −15.4% daily (2015–26); a 2008-type crisis realistically reaches −15% to −20% | always |
| B4 | **Replication:** the same months run through `backtest/backtest.py` give returns close to the live account's | average absolute gap ≤ 0.3 pp per month |
| B5 | In months when 60/40 falls, Core & Shield loses less than 60/40 (backtest norm: 72% as much). Some months will miss, so pass/fail is judged on the average across down months. | average ≤ 85% (allows for noise) |

## 3. Checkpoints
| Checkpoint | Date | Question | Pass when |
|---|---|---|---|
| **0 (operations)** | early Nov 2026 | Did October run? | O1–O8 pass for October (previous Core) |
| **1 month** | early Dec 2026 | Does the new design run? | O1–O8 all pass for November |
| **3 months** | early Feb 2027 | Is it reliable? | O1–O8 pass in 3 of 3 months; B1–B3 hold |
| **6 months** | early May 2027 | Does it behave as designed? | B1–B4 pass; B5 assessed if there were at least 2 down months for 60/40 |
| **12 months** | early Nov 2027 | Is it worth running? | See the verdict rules below |

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
- **Shadow variants** (from October 2026): `scripts/shadow.py` tracks the variants pre-registered in `config/shadow.json` every month without trading them, in `memory/SHADOW-LOG.md`. The variants are: no Bitcoin, Core 50% SPY, Core 40/10, Bitcoin as a separate 5% satellite, and (from November) gold as a 13th candidate. This gives live evidence for checkpoint decisions without resetting this evaluation. The *Live model* row against the live account is extra monthly evidence for B4. The variants are judged only at checkpoints, never adopted mid-month, and never added or changed because of results already seen.
- **Planned change: gold (GLD) as a 13th Shield candidate.** Decided by the owner on 2026-10-14, on backtest and structural grounds: it fills the "few crisis assets" gap. The known cost is a worse crash tail: 2008 −11.6% vs −7.4%.
  - It is shadow-tracked from the 2026-10 signal (November) as "+ Gold (13 candidates)".
  - **Decision rule at the early-January 2027 review** (kept as decided, independent of the restart): adopt it from the next rebalance **unless** shadow tracking shows an implementation problem: missing or stale GLD data, unexpected ranking behaviour, or a recording error.
  - Two months of returns are noise, so they are **not** a criterion either way.
  - On adoption: GLD joins `config/raam.json`, the research structural scan, the pre-flight check and the tests. This plan's change log records it, and the evaluation continues with the change noted, without restarting the clock.
- The rating (69/100 at the start) is updated at each checkpoint using these results.

## Change log
| Date | Change | Decided by |
|---|---|---|
| 2026-09-26 | Plan written before the first trade | owner |
| 2026-09-26 | IBIT added (capped at 5%) **before the first trade**. B1/B3/B5 reference numbers updated from the 2015–2026 backtest, and O8 added. Criteria otherwise unchanged. | owner |
| 2026-10-14 | Shadow tracking of 4 pre-registered variants added (`config/shadow.json`). Evidence only: criteria and the live strategy unchanged. | owner |
| 2026-10-14 | 5th shadow variant "+ Gold (13 candidates)" added, tracked from November. Planned adoption at the January checkpoint under the decision rule in section 5. Live strategy unchanged until then. | owner |
| 2026-10-14 | **Restart for the new Core** (QQQM + 10-month trend filter, live from the 2 Nov rebalance). B1 range −8.7%/+9.1%, B2 rewritten (cash can reach 100% by design), B3 set to −20% (was −14.1%, judged too tight for a realistic crisis), B5 norm 72%. Checkpoints re-dated from the 2 Nov rebalance. Pass thresholds otherwise unchanged. No result of the new design existed when this was written. | owner |
