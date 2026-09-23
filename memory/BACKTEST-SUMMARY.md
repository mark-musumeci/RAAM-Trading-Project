# Backtest Summary: historical context for the live bot

Source: `backtest/backtest.py` → [`backtest/results/REPORT.md`](../backtest/results/REPORT.md), run 2026-09-23.
It uses the live engine (`compute_signal`) with the current `config/raam.json`, Yahoo adjusted data, a signal at the month-end close and a fill at the next open, and 5 bps of cost per side.
**This is context, not a rule change.** Routines use it to judge whether a live month is normal. They never use it to alter the model.

## What RAAM (current config) historically is
- **A defensive, bond-heavy tactical allocation, not a high-return strategy.**
  - AGG and TIP were each held in 68% of months, and SHY in 51%.
  - Equities (VV, IJH, IJR, EFA, EEM) were held only 15–33% of the time each.
  - The reason: two of the three ranking factors, low volatility and low correlation, structurally favour bonds.
- **Returns, Jul-2009 → Sep-2026:**

  | | CAGR | Vol | Sharpe (rf=0) | Monthly max DD |
  |---|---|---|---|---|
  | RAAM | 4.0% | 6.3% | 0.66 | −11.8% |
  | Equal-weight 7Twelve | 7.6% | 10.8% | 0.74 | −20.2% |
  | SPY | 15.1% | 14.8% | 1.03 | −23.3% |

- It was similar in-sample (2009–19, 3.8%) and out-of-sample (2020–26, 4.4%), so there's no sign of decay, but also **no evidence of return outperformance**.
- **The paper's claim (+638% in 2004–17, about 16%/yr) is NOT reproduced** by this interpretation.
- **Where it earns its keep is crash protection:**

  | Period | RAAM | SPY | EW 7Twelve |
  |---|---|---|---|
  | 2008–09 (BWX proxy for IGOV) | +3.8% | −31.8% | −24.1% |
  | 2022 | −6.6% | −18.0% | −12.3% |

- **It lags badly in strong equity bull years:**

  | Year | RAAM | SPY |
  |---|---|---|
  | 2013 | +2.2% | +29% |
  | 2019 | +2.6% | +34% |
  | 2023 | −0.6% | +25% |
  | 2024 | −1.0% | +26% |

## Normal ranges (for judging a live month)
- **Monthly return:** 88% of months fall between −3% and +3%. The worst month was −5.4% and the best about +6%. About 62% of months are positive.
- **Daily path:** max drawdown −16.2% (2020-03-18). The worst single day was −3.1%.
- **SHY weight:** 23% on average; it reached 67% in 2022. A 40–100% SHY month is normal in falling markets.
- **Turnover:** about a third of the portfolio is replaced each month (buys + sells ≈ 64% of equity; about 3.8 one-way turns a year).

## Findings that need an owner decision (NOT applied)
1. **The circuit breaker at −15% sits right at the historical worst drawdown.** It would have tripped on 2020-03-18 (−16.2%) and 2025-04-07 (−15.4%), both near the bottom. That would have locked the portfolio in SHY through the rebounds. Consider −20%, or an automatic reset rule.
2. **The ATR trend filter (as implemented) did not help.**
   - Removing it gave Sharpe 0.81 vs 0.66 over the full period, and 0.96 vs 0.64 out-of-sample.
   - The literal lower-band reading (A3), which rarely signals long, behaves almost the same as no filter.
   - This suggests the paper's trend component (or our reading of it) adds no value.
3. **Momentum weight drives return.**
   - Momentum-only: 7.4% CAGR, 10.6% vol, which is about EW 7Twelve returns with similar risk.
   - 50/25/25: 5.7% CAGR.
   - Raising wM trades crash protection for return.
4. **Statistical caution.** Over about 17 years, the standard error on Sharpe is about ±0.25, so **none of the variant differences are statistically significant**. Choosing the best-looking variant after seeing these results is itself overfitting. Any change should be a deliberate owner decision, logged in the TRADING-STRATEGY.md change log.

## How routines should use this
- In `/monthly-review`: compare the month's RAAM return, SHY weight and drawdown with the normal ranges above. Flag anything outside them as an observation.
- Log **hypotheses**, not changes. For example: "trend filter kept VV out while VV rallied — consistent with finding 2".
- Never change config or rules based on this file.
