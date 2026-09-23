# Backtest Summary: historical context for the live bot

Source: `backtest/backtest.py` → [`backtest/results/REPORT.md`](../backtest/results/REPORT.md), run 2026-09-23. It covers the **live config after the Tier 1 upgrades**:
- BIL as cash;
- the cash-momentum hurdle;
- the −20% breaker with automatic re-entry.

It uses the live engine (`compute_signal`), Yahoo adjusted data, a signal at the month-end close and a fill at the next open, 5 bps of cost per side, and a breaker simulated on the daily path.
**This is context, not a rule change.** Routines use it to judge whether a live month is normal. They never use it to alter the model.

## What RAAM is: a defensive specialist
- **A defensive, bond-heavy tactical allocation.** AGG and TIP were each held in about 63% of months, and BIL (cash) in 56%. Equities (VV, IJH, IJR, EFA, EEM) were held only 15–33% of the time each. Two of the three ranking factors, low volatility and low correlation, structurally favour bonds.
- **Its job is defence.** On average it lost only **30% of SPY's loss in SPY's down months** (down capture). It kept 29% of SPY's gains in up months (up capture).
- **Returns, Jul-2009 → Sep-2026:**

  | | CAGR | Vol | Sharpe (rf=0) | Monthly max DD | Down capture |
  |---|---|---|---|---|---|
  | RAAM live (Tier 1) | 4.1% | 6.2% | 0.68 | −12.8% | 30% |
  | RAAM v1 (original) | 4.0% | 6.3% | 0.66 | −11.8% | 32% |
  | Equal-weight 7Twelve | 7.6% | 10.8% | 0.74 | −20.2% | 70% |
  | SPY | 15.1% | 14.8% | 1.03 | −23.3% | — |

- **Out-of-sample, 2020 → now:** the live config earned 4.8% (Sharpe 0.71, monthly max DD −7.5%). v1 earned 4.4% (Sharpe 0.64, −9.7%).
- **Crisis record:**

  | Period | RAAM live | RAAM v1 | SPY | EW 7Twelve |
  |---|---|---|---|---|
  | 2008–09 (BWX proxy for IGOV) | +1.1% | +3.8% | −31.8% | −24.1% |
  | 2022 | **−1.5%** | −6.6% | −18.0% | −12.3% |

- **It lags badly in strong equity bull years:**

  | Year | RAAM live | SPY |
  |---|---|---|
  | 2013 | +2.0% | +29% |
  | 2019 | +2.6% | +34% |
  | 2023 | −2.0% | +25% |
  | 2024 | −1.1% | +26% |

  This is the cost of the defensive specialty, not a malfunction.
- **The paper's claim (+638% in 2004–17, about 16%/yr) is NOT reproduced** by this interpretation.

## What the Tier 1 upgrades did (full detail in REPORT.md §2)
- **U2, BIL as cash:** this did most of the work. In 2022 it gave −1.5% vs −6.6%, because SHY fell with rising rates while T-bills did not. The trade-off: in 2008 SHY rallied as rates were cut, so BIL gave +1.1% vs +3.8%. **BIL defends better in inflation and rate shocks; SHY did better in deflationary crashes.**
- **U1, cash hurdle:** roughly neutral on its own (CAGR 3.9% vs 4.0%). It is kept for its principle: never hold a risk asset that is losing to cash.
- **U3, breaker at −20% with auto re-entry:** it **never tripped** in 17 years (the worst daily drawdown was −16.2% on 2020-03-18), so it costs nothing. At −15% it would have tripped once (March 2020) and cut CAGR to 3.8%.

## Normal ranges (live config; for judging a live month)
- **Monthly return:** 88% of months fall between −3% and +3%. The worst month was −5.4% and the best +5.9%. 63% of months are positive.
- **Daily path:** max drawdown −16.2% (2020-03-18). The worst day was −3.0%.
- **Cash (BIL) weight:** 25% on average. 72% on average across 2022. It was 100% cash in 7 of 207 months. A 40–100% cash month is normal in falling markets.
- **Turnover:** about a third of the portfolio is replaced each month (buys + sells ≈ 65% of equity).

## Open findings that need an owner decision (NOT applied)
1. **The ATR trend filter (as implemented) looks like a drag, even on defence.**
   - Removing it gave: CAGR 4.7% vs 4.1%, Sharpe 0.83 vs 0.68, down capture **24%** vs 30%, and daily max DD −12.0% vs −16.2%.
   - Out-of-sample it gave Sharpe 1.08 vs 0.71.
   - The literal lower-band reading (A3) behaves almost the same as no filter.
   - This is the strongest Tier 2 candidate.
2. **Momentum weight trades defence for return.** 50/25/25 gave 5.6% CAGR, but down capture was 39% and daily max DD −17.3%. For a defensive specialist, that is the wrong direction.
3. **SHY vs BIL depends on the regime** (see U2). A future option is to hold both or pick by rate trend. That's untested.
4. **Statistical caution.** Over about 17 years the standard error on Sharpe is about ±0.25, so **most variant differences are not statistically significant**. Choosing the best-looking variant after seeing results is itself overfitting. Any change should be a deliberate owner decision, logged in the TRADING-STRATEGY.md change log.

## How routines should use this
- In `/monthly-review`: compare the month's return, cash weight and drawdown with the normal ranges. Also report defence: in a month when SPY fell, what share of SPY's loss did RAAM take? The historical norm is about 30%.
- Log **hypotheses**, not changes. For example: "trend filter kept VV out while VV rallied — consistent with finding 1".
- Never change config or rules based on this file.
