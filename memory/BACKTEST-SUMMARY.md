# Backtest Summary: historical context for the live bot

Source: `backtest/backtest.py` → [`backtest/results/REPORT.md`](../backtest/results/REPORT.md), run 2026-09-24. It covers the **live config, Core & Shield**:
- the **Core**: a fixed 30% SPY + 20% AGG;
- the **Shield**: 50% RAAM, with the Tier 1 rules (BIL cash, cash-momentum hurdle) and the trend term off;
- the −20% breaker on the whole portfolio, with automatic re-entry.

It uses the live engine (`compute_signal`), Yahoo adjusted data, a signal at the month-end close and a fill at the next open, 5 bps of cost per side, and the day-by-day path.
**This is context, not a rule change.** Routines use it to judge whether a live month is normal. They never use it to alter the model.

## What Core & Shield is
A balanced portfolio whose job is to **match a 60/40's risk-adjusted return while taking much less damage in bear markets**:
- The Core supplies growth.
- The Shield (RAAM) is a defensive specialist. It moves into bonds and cash when trends weaken, and it lags in bull markets.

## Results, Jul-2009 → Sep-2026
Sharpe uses rf = 0. Against T-bills, subtract about 0.2.

| | CAGR | Vol | Sharpe | Month-end max DD | Daily max DD | 2022 |
|---|---|---|---|---|---|---|
| **Core & Shield (live)** | **7.5%** | 6.8% | **1.11** | **−11.1%** | −14.6% | **−7.8%** |
| 60/40 (SPY/AGG) | 10.2% | 9.3% | 1.09 | −19.2% | — | −15.2% |
| 30/70 (similar risk to C&S) | 6.4% | 5.8% | 1.11 | −16.3% | — | about −13% |
| Shield alone (RAAM) | 4.7% | 5.7% | 0.83 | −10.4% | −12.0% | −0.3% |
| SPY | 15.1% | 14.8% | 1.03 | −23.3% | −33.7% | −18.0% |

- **Against 60/40:** the same risk-adjusted return, with about 40% smaller drawdowns and half the 2022 loss. It earns less in total, because it takes less risk.
- **Against 30/70, the portfolio with the same risk level:** more return (7.5% vs 6.4%), a smaller worst drawdown (−11% vs −16%), and the same Sharpe.
- **By period:**

  | | 2009–19 | 2020–now |
  |---|---|---|
  | Core & Shield | 7.1% CAGR, Sharpe 1.19, month-end DD −7.1% | 8.1% CAGR, Sharpe 1.03, month-end DD −11.1% |
  | 60/40 | Sharpe 1.36 | Sharpe 0.85 |

  Core & Shield held up better once stocks and bonds began falling together.
- **The 2008 stress test** (BWX proxy for IGOV; entries Jun-08 → Jun-09): Core & Shield −7.4% vs 60/40 −17.7% and SPY −31.8%. The **breaker tripped once, on 2009-02-23 (−20.2%)**, and re-entered at the March rebalance.
- **Bull years still lag 60/40, but only moderately:**

  | Year | Core & Shield | 60/40 |
  |---|---|---|
  | 2013 | +8.9% | +16.0% |
  | 2019 | +12.9% | +23.7% |
  | 2023 | +6.7% | +16.2% |

  This is the price of the Shield.
- **The Shield alone** (for context): its 2020–now Sharpe was 1.08, and it lost −0.3% in 2022. It is excellent defence but lags badly in bull markets.

## Normal ranges (live config; for judging a live month)
- **Monthly return:** 87% of months fall between −3% and +3%. The worst month was −5.7% and the best +6.0%. 68% of months are positive.
- **Daily path:** max drawdown −14.6% (2020-03-18). The worst day was −4.2%.
- **Share of losses:**
  - In months when SPY falls, Core & Shield lost about **43% as much as SPY** and about **70% as much as 60/40**.
  - In up months, it captured about 46% of SPY's gain.
- **Cash (BIL) weight:** 14% of the portfolio on average. At most 50%, when the whole Shield is in cash; the Core stays invested. About 37% on average across 2022.
- **Turnover:** only the Shield half trades much. About 15% of the portfolio is replaced each month (buys + sells ≈ 31% of equity).

## Changes applied so far (full detail in REPORT.md §2)
- **Tier 1 (U1–U3):**
  - BIL as cash: it defends better in rate shocks; SHY did better in 2008.
  - Cash-momentum hurdle.
  - −20% breaker with auto re-entry.
- **Improvement A:** the trend term was removed. Core & Shield with the trend filter on scored worse (Sharpe 1.04 vs 1.11, daily DD −15.9% vs −14.6%).
- **Core & Shield**, 2026-09-24:
  - The 50/50 split is a preference. 70/30 (more Core) gave 8.4% CAGR, but DD −15.4% and one breaker trip.
  - 30/70 (more Shield) gave 6.4% CAGR and DD −12.2%.
  - None is statistically better; 50/50 balances growth and defence.

## Open findings that need an owner decision (NOT applied)
1. **Momentum weight in the Shield trades defence for return.** Not recommended for a defensive sleeve.
2. **SHY vs BIL depends on the regime.** Holding both, or choosing by rate trend, is untested.
3. **Inverse-volatility weighting in the Shield** looked good before 2020 and failed after. Not recommended.
4. **Fast crashes** (e.g. March 2020, −14.6%) remain the main weakness, because the Shield acts monthly. A narrow mid-month emergency exit is the candidate fix. Untested.
5. **Statistical caution.** Over about 17 years the standard error on Sharpe is about ±0.25. Most differences between variants are not significant, and choosing after seeing results is overfitting. Changes must be deliberate owner decisions, logged in TRADING-STRATEGY.md.

## How routines should use this
- In `/monthly-review`, the headline comparison is **Core & Shield against 60/40**.
  - Compare the month's return, cash weight and drawdown with the normal ranges.
  - In a month when SPY or 60/40 fell, report the share of the loss Core & Shield took. The norms are about 43% of SPY's loss and about 70% of 60/40's.
- Log **hypotheses**, not changes.
- Never change config or rules based on this file.
