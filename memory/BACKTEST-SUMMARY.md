# Backtest Summary: historical context for the live bot

Source: `backtest/backtest.py` → [`backtest/results/REPORT.md`](../backtest/results/REPORT.md), run 2026-09-23. It covers the **live config**:
- Tier 1: BIL as cash, the cash-momentum hurdle, and the −20% breaker with automatic re-entry;
- improvement A: the ATR trend term removed from the score.

It uses the live engine (`compute_signal`), Yahoo adjusted data, a signal at the month-end close and a fill at the next open, 5 bps of cost per side, and a breaker simulated on the daily path.
**This is context, not a rule change.** Routines use it to judge whether a live month is normal. They never use it to alter the model.

## What RAAM is: a defensive specialist
- **A defensive, bond-heavy tactical allocation.** Two of the three ranking factors, low volatility and low correlation, structurally favour bonds, so AGG, TIP and BIL (cash) dominate, and equities are held a minority of the time.
- **Its job is defence.** On average it took only **24% of SPY's loss in SPY's down months** while keeping 28% of SPY's gains in up months. That is a modest asymmetry in its favour.
- **Returns, Jul-2009 → Sep-2026** (monthly-based; Sharpe uses rf = 0. Against T-bills it is about 0.55):

  | | CAGR | Vol | Sharpe | Monthly max DD | Down capture |
  |---|---|---|---|---|---|
  | **RAAM live** | **4.7%** | 5.7% | **0.83** | −10.4% | **24%** |
  | RAAM v1 (original paper rules) | 4.0% | 6.3% | 0.66 | −11.8% | 32% |
  | Equal-weight 7Twelve | 7.6% | 10.8% | 0.74 | −20.2% | 70% |
  | SPY | 15.1% | 14.8% | 1.03 | −23.3% | — |

- **By period:** 2009–19 CAGR 3.6%, Sharpe 0.66. **2020–now CAGR 6.5%, Sharpe 1.08**, monthly max DD −6.2%.
- **Crisis record:**

  | Period | RAAM live | SPY | EW 7Twelve |
  |---|---|---|---|
  | 2008–09 (BWX proxy for IGOV) | +1.6% | −31.8% | −24.1% |
  | 2022 | **−0.3%** | −18.0% | −12.3% |

- **It lags badly in strong equity bull years:**

  | Year | RAAM live | SPY |
  |---|---|---|
  | 2013 | +2.0% | +29% |
  | 2019 | +3.0% | +34% |
  | 2023 | −2.2% | +25% |

  This is the cost of the defensive specialty, not a malfunction.
- **Reference point:** a fixed 30/70 SPY/AGG mix had a higher Sharpe over this period (about 1.07 at rf = 0), but lost about 14% in 2022. Most professional tactical-allocation funds trailed a 60/40 mix over the last decade.
- **The paper's claim (+638% in 2004–17, about 16%/yr) is NOT reproduced.**

## Changes applied so far (full detail in REPORT.md §2)
- **Tier 1 U2, BIL as cash:** it defends better in rate shocks (SHY fell in 2022). SHY did better in 2008, when rates were cut.
- **Tier 1 U1, cash hurdle:** roughly neutral. It's kept on principle: never hold an asset that is losing to cash.
- **Tier 1 U3, breaker at −20% with auto re-entry:** it **never tripped** in 17 years. The old −15% level would have tripped at the March 2020 low.
- **Improvement A, trend term off:**
  - CAGR 4.1% → 4.7%, daily max DD −16.2% → −12.0%, down capture 30% → 24%.
  - Sharpe out-of-sample 0.71 → 1.08.
  - It improved both the 2009–19 and the 2020–now periods.

## Normal ranges (live config; for judging a live month)
- **Monthly return:** 91% of months fall between −3% and +3%. The worst month was −4.7% and the best +5.2%. 64% of months are positive.
- **Daily path:** max drawdown −12.0% (2020-03-18). The worst day was −2.8%.
- **Cash (BIL) weight:** 27% on average. 73% on average across 2022. It was 100% cash in 7 of 207 months. A 40–100% cash month is normal in falling markets.
- **Turnover:** about 30% of the portfolio is replaced each month (buys + sells ≈ 59% of equity).
- **Defence check:** in months when SPY falls, RAAM historically lost about a quarter as much.

## Open findings that need an owner decision (NOT applied)
1. **Momentum weight trades defence for return.** 50/25/25 gave 5.9% CAGR, but down capture was 37% and daily max DD −15.2%. For a defensive specialist, that is the wrong direction.
2. **SHY vs BIL depends on the regime.** SHY did better in 2008 and BIL in 2022. Holding both, or choosing by rate trend, is untested.
3. **Inverse-volatility weighting of the picks looked good before 2020 but failed after it** (Sharpe vs T-bills 0.69 → 0.08). Not recommended.
4. **Core-satellite blend** (e.g. a 30/70 core plus RAAM) is untested. It's the most promising next idea for Sharpe.
5. **Statistical caution.** Over about 17 years the standard error on Sharpe is about ±0.25, so most variant differences are not statistically significant. Choosing the best-looking variant after seeing results is itself overfitting. Any change should be a deliberate owner decision, logged in the TRADING-STRATEGY.md change log.

## How routines should use this
- In `/monthly-review`: compare the month's return, cash weight and drawdown with the normal ranges. In a month when SPY fell, report what share of SPY's loss RAAM took; the historical norm is about 25%.
- Log **hypotheses**, not changes. For example: "momentum ranking kept equities out while SPY rallied — consistent with the bull-market lag".
- Never change config or rules based on this file.
