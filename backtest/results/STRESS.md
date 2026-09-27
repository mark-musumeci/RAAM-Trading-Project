# Stress Tests: Core & Shield (live config)

Generated 2026-09-27 by `backtest/stress.py`. Same data, engine and execution model as `backtest/backtest.py`; window 2015-04-01 → 2026-09-25. **Context only: none of this changes the strategy, the config or the evaluation criteria.**

Live baseline: CAGR 9.3%, Sharpe 1.18, daily max DD -14.1%.

## 1. Trading costs
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| 5 bps per side (live assumption) | 9.33 | 1.18 | -14.11 | 0.22 | 0.26 | 0 |
| 10 bps per side | 9.13 | 1.15 | -14.13 | 0.02 | 0.23 | 0 |
| 25 bps per side | 8.53 | 1.08 | -14.17 | -0.57 | 0.16 | 0 |
| 50 bps per side | 7.54 | 0.97 | -14.24 | -1.56 | 0.05 | 0 |

## 2. Settings neighbourhood (is the live setting a lucky peak?)
Each row changes one setting and keeps the rest live. Factor weight rows move one factor by ±10 pp and split the difference across the other two.
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| **Live settings** | 9.33 | 1.18 | -14.11 | 0.22 | 0.26 | 0 |
| Lookback 63 days (live 84) | 8.74 | 1.06 | -14.32 | -0.36 | 0.14 | 1 |
| Lookback 105 days (live 84) | 8.87 | 1.08 | -14.44 | -0.24 | 0.16 | 1 |
| Lookback 126 days (live 84) | 8.74 | 1.03 | -15.65 | -0.36 | 0.12 | 1 |
| Hold top 4 (live 5) | 8.59 | 1.13 | -15.16 | -0.52 | 0.21 | 0 |
| Hold top 6 (live 5) | 9.84 | 1.21 | -14.59 | 0.74 | 0.29 | 0 |
| EWMA λ 0.92 (live 0.94) | 8.99 | 1.14 | -14.11 | -0.11 | 0.22 | 0 |
| EWMA λ 0.97 (live 0.94) | 9.46 | 1.20 | -14.11 | 0.36 | 0.28 | 0 |
| Momentum weight +10 pp | 9.34 | 1.14 | -15.54 | 0.24 | 0.22 | 0 |
| Momentum weight -10 pp | 8.49 | 1.12 | -14.11 | -0.61 | 0.20 | 0 |
| Volatility weight +10 pp | 8.19 | 1.10 | -14.11 | -0.92 | 0.18 | 0 |
| Volatility weight -10 pp | 9.42 | 1.18 | -14.11 | 0.32 | 0.26 | 0 |
| Correlation weight +10 pp | 9.88 | 1.28 | -14.11 | 0.78 | 0.36 | 0 |
| Correlation weight -10 pp | 8.98 | 1.13 | -15.54 | -0.13 | 0.21 | 0 |

Across the 13 nudged settings: Sharpe ranges 1.03 to 1.28 (live 1.18); 13 of 13 still beat 60/40's Sharpe.

## 3. Late fills
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| 1 day after the signal (live) | 9.33 | 1.18 | -14.11 | 0.22 | 0.26 | 0 |
| 2 days after the signal | 9.39 | 1.18 | -13.60 | 0.25 | 0.26 | 0 |
| 3 days after the signal | 9.35 | 1.20 | -13.73 | 0.24 | 0.25 | 0 |
| 5 days after the signal | 9.27 | 1.23 | -13.93 | 0.25 | 0.16 | 0 |

## 4. Rolling 12-month windows vs 60/40 (what a single year can look like)
- 127 overlapping windows. Core & Shield returned more than 60/40 in **49%** of them.
- 12-month gap vs 60/40: median -0.1 pp; 1 in 10 windows was worse than -5.4 pp, 1 in 10 better than +6.7 pp.
- Worst 12 months: C&S -8.8% vs 60/40 -15.2%. Best: C&S 33.6% vs 60/40 35.2%.
- C&S had a negative 12 months in 12% of windows.
- C&S had the smaller drawdown inside the window in **89%** of windows.
- In the 14 windows where 60/40 lost money, C&S did better in 93%; when 60/40 rose, C&S did better in 43%.

## 5. Monte Carlo (5,000 paths, 6-month blocks of live monthly returns, paired with 60/40)
Month-end values, so drawdowns are shallower than the daily path (the backtest's daily worst was −14.1% vs −11.1% month-end). Resampling history can't create crises that never happened; section 6 covers that.

| Measure | Core & Shield | 60/40 |
|---|---|---|
| 10-year CAGR, 5th / 50th / 95th percentile | 4.9% / 9.3% / 13.7% | 4.4% / 9.2% / 13.6% |
| 10-year Sharpe, 5th / 50th / 95th | 0.64 / 1.18 / 1.74 | 0.45 / 0.94 / 1.48 |
| 10-year max drawdown: typical / 1-in-20 / 1-in-100 | -9.9% / -16.7% / -20.9% | -14.5% / -24.8% / -30.9% |

- Chance over 10 years of a month-end drawdown worse than −11.1%: 36%; worse than −14.1%: 14%; worse than −20%: 1.4%.
- Chance of a higher 10-year Sharpe than 60/40: **94%**; of a smaller 10-year drawdown than 60/40: **97%**.
- Any single year: 52% chance of trailing 60/40, 14% chance of a loss. 1-year return 5th / 50th / 95th: -4.2% / +9.1% / +23.8%.

## 6. Synthetic shocks worse than history
Each shock is injected into the price data at several dates (a permanent level shift; prices then follow their real path) and the full model is rerun, so the model reacts as it would live. Loss = worst point from the day before the shock to 63 trading days after it ends. 'No-shock' is the same window without the shock. 60/40 is buy-and-hold from the day before.

### Crash day (1987-style, −20% equities and Bitcoin in one day)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -9.0% | 0.4% | -9.3 pp | -13.3% | tripped 2016-11-15 | 117 |
| 2017-09-15 | -8.5% | 0.6% | -9.1 pp | -14.1% | tripped 2017-09-15 | 57 |
| 2019-07-15 | -10.0% | -2.2% | -7.8 pp | -17.7% | tripped 2019-07-15 | 231 |
| 2021-06-15 | -10.8% | -1.8% | -9.0 pp | -17.2% | tripped 2021-06-15 | 745 |
| 2023-11-15 | -7.2% | -0.1% | -7.1 pp | -16.5% | tripped 2023-11-15 | 75 |
| 2025-08-15 | -10.3% | -0.8% | -9.5 pp | -18.3% | tripped 2025-08-15 | 187 |

Average loss: C&S -9.3% vs 60/40 -16.2% (C&S took 57% of 60/40's loss). Worst: C&S -10.8%, 60/40 -18.3%.

### Stocks and bonds fall together (equities −25%, bonds −15% over 6 months)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -6.3% | 0.4% | -6.7 pp | -16.2% | no | 79 |
| 2017-09-15 | -6.8% | 0.6% | -7.3 pp | -20.1% | no | 280 |
| 2019-07-15 | -21.3% | -10.2% | -11.1 pp | -35.4% | tripped 2020-03-18 | 193 |
| 2021-06-15 | -13.0% | -1.8% | -11.2 pp | -24.5% | no | 628 |
| 2023-11-15 | -5.8% | -0.1% | -5.7 pp | -13.4% | no | 93 |
| 2025-08-15 | -8.5% | -0.8% | -7.7 pp | -24.1% | no | not yet |

Average loss: C&S -10.3% vs 60/40 -22.3% (C&S took 46% of 60/40's loss). Worst: C&S -21.3%, 60/40 -35.4%.

### Stagflation (equities −20%, AGG/IGOV −10%, TIP +3%, DBC +25% over 6 months)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -3.2% | 0.4% | -3.5 pp | -10.8% | no | 40 |
| 2017-09-15 | -2.0% | 0.6% | -2.6 pp | -15.0% | no | 28 |
| 2019-07-15 | -16.9% | -10.2% | -6.7 pp | -31.2% | no | 116 |
| 2021-06-15 | -8.1% | -1.8% | -6.3 pp | -19.6% | no | 508 |
| 2023-11-15 | -2.2% | -0.1% | -2.2 pp | -8.2% | no | 10 |
| 2025-08-15 | -3.0% | -0.8% | -2.2 pp | -19.2% | no | 10 |

Average loss: C&S -5.9% vs 60/40 -17.3% (C&S took 34% of 60/40's loss). Worst: C&S -16.9%, 60/40 -31.2%.

### Bitcoin −80% in a month while IBIT is held

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2015-08-10 | -6.5% | -3.9% | -2.6 pp | -6.6% | no | 173 |
| 2016-11-08 | -3.4% | -0.0% | -3.4 pp | 0.3% | no | 49 |
| 2018-02-08 | -2.9% | -1.0% | -1.9 pp | -2.8% | no | 35 |
| 2020-09-09 | -3.8% | -0.9% | -2.9 pp | -2.1% | no | 6 |
| 2023-06-08 | -5.1% | -1.5% | -3.6 pp | -1.2% | no | 50 |
| 2025-03-10 | -9.6% | -6.5% | -3.1 pp | -11.6% | no | 54 |

Average extra loss from the Bitcoin crash: -2.9 pp (worst -3.6 pp). 60/40 isn't exposed, so it isn't a fair comparison here.

