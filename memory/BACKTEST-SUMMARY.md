# Backtest Summary: historical context for the live bot

Source: `backtest/backtest.py` → [`backtest/results/REPORT.md`](../backtest/results/REPORT.md), rerun 2026-10-14 for the **live config from the 2026-10 signal**:
- the **Core**: 50% **QQQM** (Nasdaq-100) while its month-end close is above its 10-month average, otherwise BIL (T-bills). QQQM before its Oct 2020 launch is QQQ, the same index;
- the **Shield**: 50% RAAM over **12 candidates, including IBIT (a spot-Bitcoin ETF)**, with IBIT capped at **5% of the whole portfolio**;
- the Tier 1 rules, the trend term off, and the −20% breaker on the whole portfolio.

It uses the live engine (`compute_signal`), a signal at the month-end close and a fill at the next open, 5 bps of cost per side, and the day-by-day path. Before IBIT launched (Jan 2024), IBIT = BTC-USD aligned to US trading days, minus a 0.25%/yr fee, spliced into real IBIT. That makes the comparison window **Feb 2015 → Sep 2026**.
**This is context, not a rule change.** Routines use it to judge whether a live month is normal. They never use it to alter the model.

## Current design: QQQM trend Core + Shield (live from the 2 Nov 2026 rebalance)
Figures from `backtest/results/readme_metrics.json` (`docs/readme_metrics.py`); T-bills returned 2.0%/yr.

| Feb 2015 → Sep 2026 | **Live (QQQM trend Core)** | Live without IBIT | Previous (60/40 Core) | 60/40 | SPY |
|---|---|---|---|---|---|
| Return / yr | **11.9%** | 9.0% | 9.3% | 9.2% | 14.1% |
| Volatility | 9.7% | 9.0% | 7.8% | 10.0% | 15.6% |
| Sharpe vs T-bills | **1.01** | 0.79 | 0.93 | 0.73 | 0.81 |
| Sortino vs T-bills | **1.77** | 1.28 | 1.58 | 1.11 | 1.24 |
| Calmar | **1.02** | 0.74 | 0.84 | 0.48 | 0.61 |
| Worst month-end drawdown | −11.7% | −12.2% | −11.1% | −19.2% | −23.3% |
| Worst daily drawdown | −15.4% | −16.1% | −14.1% | — | −33.7% |
| Months to recover the worst drawdown | 4 | 4 | 16 | 16 | 15 |
| Share of 60/40's down-month losses | 72% | 74% | 63% | 100% | — |
| Beta to 60/40 / alpha vs T-bills | 0.68 / +4.9%/yr (t 2.3) | 0.64 / +2.4%/yr (t 1.3) | 0.69 / +2.2%/yr | 1.00 | — |
| 2022 | **−4.9%** | — | −8.8% | −15.2% | −18.0% |

- **2008–2026 without Bitcoin:** 8.8%/yr vs 6.6% (previous design) and 8.5% (60/40). Sharpe vs T-bills 0.85 vs 0.74 and 0.72; Calmar **0.72** vs 0.35 and 0.28. Worst month-end drawdown −12.2% vs −19.0% and −30.2%. Jun 2008–Jun 2009 about −1% vs −7.4% and −17.7%.
- **By period:** better than the previous design in 2020–26 (Calmar 1.12 vs 0.83) and slightly **worse in 2015–19** (1.17 vs 1.32). The gain is concentrated in the tech-led 2020s and in stepping aside in 2022.
- **Bitcoin dependence is much lower:** without IBIT it still returns 9.0%/yr (previous design 6.5%).
- **Known risk outside the data:** a tech-led bust. In 2000–02 the trend-filtered Nasdaq-100 alone fell about 36% before stepping aside. Inside this portfolio that is roughly an extra −18%. Over 1999–2026 a trend-filtered S&P 500 had the better Calmar (0.33 vs 0.26); the Nasdaq-100's edge is a 2010s-era result.
- **The trend filter matters:** QQQM with no filter would have had a −24.6% worst day and 65% down capture vs SPY.
- **Skill test** (`backtest/robustness.py`): the full strategy beats **99%** of 1,000 random-pick Shield portfolios on Sharpe in both 2015–26 and 2008–26, and 98–100% on down-market defence and worst day.

### Normal ranges (current design, for judging a live month)
- **Monthly return:** 70% of months between −3% and +3%, 81% between −4% and +4%. Worst month −8.7%, best +9.1%. 66% of months positive.
- **Drawdown:** worst month-end −11.7%, worst daily −15.4% (March 2020, when the −5% daily breaker tripped once). A 2008-type crisis realistically reaches −15% to −20%.
- **Share of losses:** in 60/40's down months it lost about **72%** as much.
- **Cash (BIL):** 26% on average. It can reach **100%** when the Core trend filter is off and the whole Shield is in cash (2022 averaged 83%).
- **Core trend filter:** off (Core in T-bills) in about 1 month in 5.
- **Turnover:** about 21% of the portfolio a month (5.1× a year two-sided), ≈0.25%/yr at 5 bps.
- **IBIT:** never above 5% at a rebalance.

---

**Everything below describes the previous design (fixed 60/40 Core, live 1–31 Oct 2026)** and the tests that led here. It is kept as history; its "Normal ranges" no longer apply.

## What Core & Shield was (previous design)
A balanced portfolio that aims to **match or beat a 60/40's risk-adjusted return while taking much less damage in bear markets**:
- The Core supplies growth.
- The Shield (RAAM) is a defensive rotation with a small, capped Bitcoin sleeve. It moves into bonds and cash when trends weaken, and it lags in strong equity bull markets.

## Results, Feb 2015 → Sep 2026
Sharpe uses rf = 0.

| | CAGR | Vol | Sharpe | Month-end max DD | Daily max DD | 2022 |
|---|---|---|---|---|---|---|
| **Core & Shield + IBIT capped 5% (live)** | **9.3%** | 7.8% | **1.18** | −11.1% | **−14.1%** | −8.8% |
| Core & Shield without IBIT (previous live) | 6.5% | 6.9% | 0.95 | −11.1% | −14.6% | about −8% |
| Core & Shield + IBIT uncapped (10% slots) | 12.7% | 10.0% | 1.25 | — | −15.3% | — |
| IBIT flattened to 0%/yr (hindsight check) | 7.6% | 7.5% | 1.01 | — | −14.6% | — |
| 60/40 (SPY/AGG) | 9.2% | 10.0% | 0.93 | −19.2% | — | −15.2% |
| SPY | 14.1% | 15.6% | 0.93 | −23.3% | −33.7% | −18.0% |

**Risk-adjusted and downside ratios** (from `backtest/results/readme_metrics.json`, built by `docs/readme_metrics.py`; T-bills returned 2.0%/yr):

| | Sharpe vs T-bills | Sortino vs T-bills | Calmar |
|---|---|---|---|
| **Core & Shield (live)** | **0.93** | **1.58** | **0.84** |
| Core & Shield without IBIT | 0.66 | 1.00 | 0.59 |
| 60/40 | 0.73 | 1.11 | 0.48 |
| SPY | 0.81 | 1.24 | 0.61 |
| *2008–2026, without Bitcoin:* C&S / 60/40 / SPY | 0.74 / 0.72 / 0.70 | 1.14 / 1.06 / 1.02 | 0.35 / 0.28 / 0.25 |

- **Definitions:** Sortino = annual return above T-bills ÷ downside deviation (months below T-bills only). Calmar = annual return ÷ worst month-end drawdown over the whole window.
- **Reading them:** the strategy's lead is largest on Sortino and Calmar, which only count losses. That is consistent with its job of limiting losses, not maximising return.

- **Against 60/40:** about the same return (9.3% vs 9.2%), a **higher Sharpe** (1.18 vs 0.93) and a **much smaller month-end drawdown** (−11% vs −19%).
- **2020–now:** 9.2% CAGR, Sharpe 1.08 (without IBIT: 8.1%, 1.03; 60/40: 9.5%, 0.85).
- **Hindsight check:** even with Bitcoin flattened to a 0% long-run return, the strategy earned 7.6% vs 6.5% without IBIT. About half the IBIT benefit is timing (riding trends and exiting crashes), and about half is Bitcoin's actual rise. **Don't count on the second half repeating.**
- **Calendar years:**

  | Year | C&S | 60/40 |
  |---|---|---|
  | 2017 | +28.9% | +14.1% |
  | 2018 | −7.0% | −3.3% |
  | 2019 | +19.6% | +23.7% |
  | 2022 | −8.8% | −15.2% |
  | 2023 | +8.8% | +16.2% |
  | 2024 | +13.5% | +16.1% |

  The crypto winters (2018, 2022) cost more than without IBIT. The equity bull years still lag 60/40.
- **2008 stress test** (without IBIT, since Bitcoin didn't exist): C&S −7.4% vs 60/40 −17.7%. The breaker tripped once, on 2009-02-23 (−20.2%).
- **The paper's claim (+638% in 2004–17) is NOT reproduced**, and Core & Shield is our own evolution of it.

## Normal ranges (previous design; superseded)
- **Monthly return:** 78% of months fall between −3% and +3%. The worst month was −5.7% and the best +6.9%. 65% of months are positive.
- **Daily path:** max drawdown −14.1% (2020-03-18). The worst day was −4.2%.
- **Share of losses:** in months when 60/40 falls, Core & Shield lost about **63%** as much. In SPY's down months, it lost about 42% as much.
- **Cash (BIL) weight:** 16% of the portfolio on average. At most 50%, when the whole Shield is in cash. It's 37% on average in a year like 2022.
- **IBIT:** held (at the 5% cap) in about 52% of months. **It never exceeds 5% at a rebalance.** Between rebalances it can drift up or down with Bitcoin.
- **Turnover:** about 15% of the portfolio is replaced each month.

## Changes applied so far (full detail in REPORT.md §2)
- **Tier 1:** BIL as cash, the cash-momentum hurdle, and the −20% breaker with auto re-entry.
- **Improvement A:** the trend term was removed.
- **Core & Shield** (2026-09-24): the 50/50 split.
- **IBIT capped at 5%** (2026-09-26), before the first trade.

## Tested and rejected, or parked (2026-09-26 tests)
- **Swapping VV→TLT and VAW→GLD**, and **core-aware correlation**:
  - they looked good before 2020 but **did worse from 2020 onward**;
  - the swap also made March 2020 (−18.7%) and 2008 (−13.9%) worse.
  - **Rejected.**
- **Vol-managed Core** (SPY scaled by 15% ÷ 21-day volatility):
  - shallower losses in every crisis tested;
  - the same Sharpe, about 0.7%/yr less return.
  - **Parked** as a preference option.
- **Inverse-volatility sizing:** failed from 2020 onward. **Rejected.**
- **Momentum-heavy weights:** trade defence for return. Not recommended.
- **Statistical caution:** over about 11 years the standard error on Sharpe is about ±0.3, so **most differences are not statistically significant**. Changes must be deliberate owner decisions, logged in TRADING-STRATEGY.md.

## Stress tests (2026-09-27, `backtest/stress.py` → [`backtest/results/STRESS.md`](../backtest/results/STRESS.md))
Context only. These changed nothing in the strategy or the evaluation criteria.
- **Costs:** the Sharpe edge over 60/40 survives even 50 bps per side (0.97 vs 0.93). The CAGR edge disappears above about 10 bps. Live slippage above 10 bps (O6) would therefore cost return, not the risk-adjusted case.
- **Settings neighbourhood:** 13 of 13 nudged settings still beat 60/40's Sharpe (range 1.03–1.28). It isn't a lucky peak. Longer or shorter lookbacks are slightly worse, and nothing collapses.
- **Late fills:** filling 2–5 days late barely changes the result (Sharpe 1.18–1.23). A missed or delayed rebalance is cheap, which supports "halt when in doubt".
- **Any single 12 months:**
  - C&S beat 60/40 in only **49%** of rolling windows. Median gap −0.1 pp; 1 in 10 years is worse than −5.4 pp.
  - It had the smaller drawdown in **89%** of windows, and beat 60/40 in 93% of the windows where 60/40 lost money.
  - Expect a coin flip on return in any year. The defence is the reliable part.
- **Monte Carlo (5,000 10-year paths, month-end):**
  - P(Sharpe above 60/40) 94%; P(smaller drawdown) 97%.
  - P(month-end drawdown worse than −14.1%) 14%, worse than −20% 1.4%.
  - Any single year: 52% chance of trailing 60/40, 14% chance of a loss.
- **Synthetic shocks, worse than history:**
  - **Crash day** (−20% equities and Bitcoin): about −9%, versus −16% for 60/40. The −5% daily breaker trips every time, so the portfolio sits in cash until the next rebalance and can miss a quick rebound.
  - **Stocks and bonds falling together over 6 months:** −10% on average, versus −22% for 60/40. Stacked on top of a real crash (the 2019-07 start, which runs into Covid), it reached **−21%**, tripping the −20% breaker. That is the realistic worst case.
  - **Stagflation:** −6%, versus −17% for 60/40.
  - **Bitcoin −80% while IBIT is held:** about −3 pp extra, as the 5% cap intends.
- **Failure drills (`tests/test_faults.py`):**
  - Rejected orders, partial fills, API errors, missing or stale data and zero prices all end in a halt with no wrong trade. Buys never exceed available cash.
  - Two findings, both **fixed on 2026-10-14** (owner approved; tests now pass):
    - **F1:** sells that filled before a mid-rebalance API error were not logged. Now the completed orders and the failed one are written to TRADE-LOG and the signal file, and the run halts.
    - **F2:** a blank (NaN) latest close was silently replaced by the previous day's close. Now any blank or non-positive close in the lookback window halts the signal.

## Robustness (2026-10-14, `backtest/robustness.py` → [`backtest/results/ROBUSTNESS.md`](../backtest/results/ROBUSTNESS.md))
Context only. These changed nothing in the strategy or the evaluation criteria.
- **Does the ranking have skill?** The live ranking was compared with 1,000 portfolios whose Shield holds 5 *random* candidates each month, with every other rule identical.
  - It beat **94–98%** of them on Sharpe and **97–100%** on down-market defence, in both windows (2015–26 with Bitcoin; 2008–26 without), at portfolio level and for the Shield alone.
  - On raw return it beat 63–98%. On the worst single day it beat only about half: a monthly model can't react to a one-day crash.
  - **The edge is real, and it is mainly defence and risk-adjusted return.**
- **Which parts matter:**
  - *Momentum only* (top 5 by momentum) earns more but defends much worse: 83% of 60/40's down-month losses against 63%, and a worst daily drop of −17.7% against −14.1%. The volatility and correlation ranks are what make it defensive.
  - *No ranking* (all 12 with the cash test) matched the Sharpe in 2015–26 but trailed over 2008–26 (0.84 vs 0.93) and defended worse. The cash test does a lot of the work; the ranking adds defence on top.
- **Long history without Bitcoin (Mar 2008 → Sep 2026, 223 months, IGOV extended with BWX):**

  | | C&S (no Bitcoin) | 60/40 | SPY |
  |---|---|---|---|
  | Return / yr | 6.6% | 8.5% | 12.0% |
  | Sharpe | 0.93 | 0.85 | 0.78 |
  | Worst month-end drop | −19.0% | −30.2% | −47.2% |

  - Worst daily drop **−22.0%** (9 Mar 2009). The breaker tripped once (23 Feb 2009).
  - Crisis years: 2008 −11.4% against 60/40's −17.2%; 2022 −7.8% against −15.2%.
  - Bull years lag badly: 2015–19 returned 4.2%/yr against 8.4%. It was ahead of 60/40 in only 5 of 19 calendar years, and beat it in 23% of rolling 12-month windows.
- **For judging live months:**
  - Without Bitcoin's contribution, expect a defensive product: about 2%/yr below 60/40 in normal markets, with roughly a third smaller drawdowns.
  - **A 2008-type crisis realistically means about −20% to −22%.** That is worse than the −14.1% in "Normal ranges", and the strategy would still be working as designed.

## How routines should use this
- In `/monthly-review`, the headline comparison is **Core & Shield against 60/40**. Compare the month's return, cash weight and drawdown with the normal ranges. When 60/40 fell, report the share of its loss that C&S took (the norm is about 63%).
- In months when Bitcoin moves sharply, note IBIT's contribution separately.
- Log **hypotheses**, not changes. Never change config or rules based on this file.
