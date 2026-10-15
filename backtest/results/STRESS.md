# Stress Tests: Core & Shield (live config)

Generated 2026-10-14 by `backtest/stress.py`. Same data, engine and execution model as `backtest/backtest.py`; window 2015-04-01 → 2026-09-25. **Context only: none of this changes the strategy, the config or the evaluation criteria.**

Live baseline: CAGR 11.9%, Sharpe 1.20, daily max DD -15.4%.

## 1. Trading costs
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| 5 bps per side (live assumption) | 11.86 | 1.20 | -15.39 | 2.76 | 0.28 | 1 |
| 10 bps per side | 11.57 | 1.18 | -15.49 | 2.47 | 0.26 | 1 |
| 25 bps per side | 10.70 | 1.09 | -15.90 | 1.60 | 0.17 | 1 |
| 50 bps per side | 9.26 | 0.95 | -16.61 | 0.16 | 0.04 | 1 |

## 2. Settings neighbourhood (is the live setting a lucky peak?)
Each row changes one setting and keeps the rest live. Factor weight rows move one factor by ±10 pp and split the difference across the other two.
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| **Live settings** | 11.86 | 1.20 | -15.39 | 2.76 | 0.28 | 1 |
| Lookback 63 days (live 84) | 11.43 | 1.12 | -17.40 | 2.32 | 0.20 | 1 |
| Lookback 105 days (live 84) | 11.57 | 1.15 | -17.97 | 2.46 | 0.24 | 1 |
| Lookback 126 days (live 84) | 12.15 | 1.23 | -12.86 | 3.05 | 0.31 | 1 |
| Hold top 4 (live 5) | 11.11 | 1.17 | -16.16 | 2.01 | 0.25 | 1 |
| Hold top 6 (live 5) | 12.19 | 1.19 | -17.76 | 3.08 | 0.27 | 1 |
| EWMA λ 0.92 (live 0.94) | 11.52 | 1.17 | -15.39 | 2.42 | 0.26 | 1 |
| EWMA λ 0.97 (live 0.94) | 12.00 | 1.22 | -15.39 | 2.90 | 0.30 | 1 |
| Momentum weight +10 pp | 11.88 | 1.18 | -16.82 | 2.77 | 0.26 | 1 |
| Momentum weight -10 pp | 11.00 | 1.14 | -15.42 | 1.90 | 0.22 | 1 |
| Volatility weight +10 pp | 10.69 | 1.12 | -15.42 | 1.58 | 0.20 | 1 |
| Volatility weight -10 pp | 11.96 | 1.21 | -15.39 | 2.86 | 0.29 | 1 |
| Correlation weight +10 pp | 12.43 | 1.27 | -15.39 | 3.32 | 0.36 | 1 |
| Correlation weight -10 pp | 11.50 | 1.16 | -16.82 | 2.40 | 0.24 | 1 |

Across the 13 nudged settings: Sharpe ranges 1.12 to 1.27 (live 1.20); 13 of 13 still beat 60/40's Sharpe.

## 3. Late fills
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| 1 day after the signal (live) | 11.86 | 1.20 | -15.39 | 2.76 | 0.28 | 1 |
| 2 days after the signal | 11.65 | 1.15 | -14.76 | 2.52 | 0.23 | 1 |
| 3 days after the signal | 11.42 | 1.11 | -14.93 | 2.31 | 0.15 | 1 |
| 5 days after the signal | 10.78 | 1.08 | -16.66 | 1.76 | 0.02 | 1 |

## 4. Rolling 12-month windows vs 60/40 (what a single year can look like)
- 127 overlapping windows. Core & Shield returned more than 60/40 in **59%** of them.
- 12-month gap vs 60/40: median +2.5 pp; 1 in 10 windows was worse than -6.6 pp, 1 in 10 better than +14.4 pp.
- Worst 12 months: C&S -7.7% vs 60/40 -15.2%. Best: C&S 46.5% vs 60/40 35.2%.
- C&S had a negative 12 months in 13% of windows.
- C&S had the smaller drawdown inside the window in **59%** of windows.
- In the 14 windows where 60/40 lost money, C&S did better in 100%; when 60/40 rose, C&S did better in 54%.

## 5. Monte Carlo (5,000 paths, 6-month blocks of live monthly returns, paired with 60/40)
Month-end values, so drawdowns are shallower than the daily path (the backtest's daily worst was -15.4%). Resampling history can't create crises that never happened; section 6 covers that.

| Measure | Core & Shield | 60/40 |
|---|---|---|
| 10-year CAGR, 5th / 50th / 95th percentile | 6.4% / 11.8% / 17.6% | 4.4% / 9.2% / 13.6% |
| 10-year Sharpe, 5th / 50th / 95th | 0.70 / 1.21 / 1.73 | 0.45 / 0.94 / 1.48 |
| 10-year max drawdown: typical / 1-in-20 / 1-in-100 | -11.7% / -18.6% / -22.7% | -14.5% / -24.8% / -30.9% |

- Chance over 10 years of a month-end drawdown worse than −11.1%: 67%; worse than −14.1%: 25%; worse than −20%: 3.0%.
- Chance of a higher 10-year Sharpe than 60/40: **89%**; of a smaller 10-year drawdown than 60/40: **80%**.
- Any single year: 38% chance of trailing 60/40, 13% chance of a loss. 1-year return 5th / 50th / 95th: -4.9% / +11.2% / +31.2%.

## 6. Synthetic shocks worse than history
Each shock is injected into the price data at several dates (a permanent level shift; prices then follow their real path) and the full model is rerun, so the model reacts as it would live. Loss = worst point from the day before the shock to 63 trading days after it ends. 'No-shock' is the same window without the shock. 60/40 is buy-and-hold from the day before.

### Crash day (1987-style, −20% equities and Bitcoin in one day)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -12.4% | 0.8% | -13.1 pp | -13.3% | tripped 2016-11-15 | 182 |
| 2017-09-15 | -12.4% | 0.1% | -12.5 pp | -14.1% | tripped 2017-09-15 | 570 |
| 2019-07-15 | -13.5% | -4.0% | -9.5 pp | -17.7% | tripped 2019-07-15 | 309 |
| 2021-06-15 | -15.1% | -1.5% | -13.7 pp | -17.2% | tripped 2021-06-15 | 616 |
| 2023-11-15 | -11.3% | -0.1% | -11.2 pp | -16.5% | tripped 2023-11-15 | 264 |
| 2025-08-15 | -14.4% | -1.7% | -12.7 pp | -18.3% | tripped 2025-08-15 | not yet |

Average loss: C&S -13.2% vs 60/40 -16.2% (C&S took 81% of 60/40's loss). Worst: C&S -15.1%, 60/40 -18.3%.

### Stocks and bonds fall together (equities −25%, bonds −15% over 6 months)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -2.1% | 0.8% | -2.8 pp | -16.2% | no | 28 |
| 2017-09-15 | -1.4% | 0.1% | -1.5 pp | -20.1% | no | 12 |
| 2019-07-15 | -10.6% | -6.6% | -4.0 pp | -35.4% | no | 194 |
| 2021-06-15 | -9.3% | -1.5% | -7.9 pp | -24.5% | no | 361 |
| 2023-11-15 | -3.5% | -0.1% | -3.4 pp | -13.4% | no | 53 |
| 2025-08-15 | -7.6% | -1.7% | -5.8 pp | -24.1% | no | 208 |

Average loss: C&S -5.7% vs 60/40 -22.3% (C&S took 26% of 60/40's loss). Worst: C&S -10.6%, 60/40 -35.4%.

### Stagflation (equities −20%, AGG/IGOV −10%, TIP +3%, DBC +25% over 6 months)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -1.6% | 0.8% | -2.4 pp | -10.8% | no | 9 |
| 2017-09-15 | -2.2% | 0.1% | -2.2 pp | -15.0% | no | 4 |
| 2019-07-15 | -9.5% | -6.6% | -2.8 pp | -31.2% | no | 184 |
| 2021-06-15 | -5.1% | -1.5% | -3.6 pp | -19.6% | no | 320 |
| 2023-11-15 | -6.9% | -0.1% | -6.8 pp | -8.2% | no | 47 |
| 2025-08-15 | -4.2% | -1.7% | -2.5 pp | -19.2% | no | 71 |

Average loss: C&S -4.9% vs 60/40 -17.3% (C&S took 28% of 60/40's loss). Worst: C&S -9.5%, 60/40 -31.2%.

### Bitcoin −80% in a month while IBIT is held

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2015-08-10 | -10.1% | -6.6% | -3.6 pp | -6.6% | no | 324 |
| 2016-11-08 | -4.1% | -0.8% | -3.3 pp | 0.3% | no | 29 |
| 2018-02-08 | -3.3% | -1.9% | -1.4 pp | -2.8% | no | 11 |
| 2020-09-09 | -3.7% | -1.1% | -2.7 pp | -2.1% | no | 12 |
| 2023-06-08 | -3.1% | 0.5% | -3.6 pp | -1.2% | no | 30 |
| 2025-03-10 | -8.0% | -4.7% | -3.3 pp | -11.6% | no | 70 |

Average extra loss from the Bitcoin crash: -3.0 pp (worst -3.6 pp). 60/40 isn't exposed, so it isn't a fair comparison here.

