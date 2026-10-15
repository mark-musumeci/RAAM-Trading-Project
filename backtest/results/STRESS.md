# Stress Tests: Core & Shield (live config)

Generated 2026-10-15 by `backtest/stress.py`. Same data, engine and execution model as `backtest/backtest.py`; window 2015-04-01 → 2026-09-25. **Context only: none of this changes the strategy, the config or the evaluation criteria.**

Live baseline: CAGR 11.7%, Sharpe 1.19, daily max DD -15.4%.

## 1. Trading costs
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| 5 bps per side (live assumption) | 11.75 | 1.19 | -15.43 | 2.65 | 0.27 | 1 |
| 10 bps per side | 11.46 | 1.17 | -15.53 | 2.35 | 0.25 | 1 |
| 25 bps per side | 10.58 | 1.08 | -15.94 | 1.48 | 0.16 | 1 |
| 50 bps per side | 9.14 | 0.94 | -16.66 | 0.04 | 0.03 | 1 |

## 2. Settings neighbourhood (is the live setting a lucky peak?)
Each row changes one setting and keeps the rest live. Factor weight rows move one factor by ±10 pp and split the difference across the other two.
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| **Live settings** | 11.75 | 1.19 | -15.43 | 2.65 | 0.27 | 1 |
| Lookback 63 days (live 84) | 11.32 | 1.12 | -17.44 | 2.22 | 0.20 | 1 |
| Lookback 105 days (live 84) | 11.72 | 1.17 | -18.01 | 2.62 | 0.25 | 1 |
| Lookback 126 days (live 84) | 12.30 | 1.25 | -12.86 | 3.20 | 0.33 | 1 |
| Hold top 4 (live 5) | 11.03 | 1.15 | -16.21 | 1.92 | 0.24 | 1 |
| Hold top 6 (live 5) | 12.38 | 1.23 | -16.07 | 3.28 | 0.31 | 1 |
| EWMA λ 0.92 (live 0.94) | 11.42 | 1.17 | -15.43 | 2.31 | 0.25 | 1 |
| EWMA λ 0.97 (live 0.94) | 11.92 | 1.21 | -15.43 | 2.81 | 0.29 | 1 |
| Momentum weight +10 pp | 11.83 | 1.18 | -16.86 | 2.73 | 0.26 | 1 |
| Momentum weight -10 pp | 10.94 | 1.14 | -15.46 | 1.84 | 0.22 | 1 |
| Volatility weight +10 pp | 10.28 | 1.08 | -15.46 | 1.17 | 0.16 | 1 |
| Volatility weight -10 pp | 11.95 | 1.21 | -15.43 | 2.84 | 0.29 | 1 |
| Correlation weight +10 pp | 12.42 | 1.28 | -15.43 | 3.32 | 0.36 | 1 |
| Correlation weight -10 pp | 11.48 | 1.16 | -16.86 | 2.38 | 0.24 | 1 |

Across the 13 nudged settings: Sharpe ranges 1.08 to 1.28 (live 1.19); 13 of 13 still beat 60/40's Sharpe.

## 3. Late fills
| Variant | CAGR % | Sharpe | MaxDD % (daily) | CAGR − 60/40 pp | Sharpe − 60/40 | Breaker trips |
|---|---|---|---|---|---|---|
| 1 day after the signal (live) | 11.75 | 1.19 | -15.43 | 2.65 | 0.27 | 1 |
| 2 days after the signal | 11.57 | 1.14 | -14.82 | 2.44 | 0.22 | 1 |
| 3 days after the signal | 11.34 | 1.10 | -14.98 | 2.23 | 0.15 | 1 |
| 5 days after the signal | 10.72 | 1.07 | -16.66 | 1.70 | 0.01 | 1 |

## 4. Rolling 12-month windows vs 60/40 (what a single year can look like)
- 127 overlapping windows. Core & Shield returned more than 60/40 in **58%** of them.
- 12-month gap vs 60/40: median +1.7 pp; 1 in 10 windows was worse than -6.7 pp, 1 in 10 better than +14.5 pp.
- Worst 12 months: C&S -7.7% vs 60/40 -15.2%. Best: C&S 46.8% vs 60/40 35.2%.
- C&S had a negative 12 months in 13% of windows.
- C&S had the smaller drawdown inside the window in **59%** of windows.
- In the 14 windows where 60/40 lost money, C&S did better in 100%; when 60/40 rose, C&S did better in 53%.

## 5. Monte Carlo (5,000 paths, 6-month blocks of live monthly returns, paired with 60/40)
Month-end values, so drawdowns are shallower than the daily path (the backtest's daily worst was -15.4%). Resampling history can't create crises that never happened; section 6 covers that.

| Measure | Core & Shield | 60/40 |
|---|---|---|
| 10-year CAGR, 5th / 50th / 95th percentile | 6.3% / 11.7% / 17.4% | 4.4% / 9.2% / 13.6% |
| 10-year Sharpe, 5th / 50th / 95th | 0.69 / 1.20 / 1.72 | 0.45 / 0.94 / 1.48 |
| 10-year max drawdown: typical / 1-in-20 / 1-in-100 | -11.7% / -18.6% / -22.7% | -14.5% / -24.8% / -30.9% |

- Chance over 10 years of a month-end drawdown worse than −11.1%: 68%; worse than −14.1%: 25%; worse than −20%: 3.1%.
- Chance of a higher 10-year Sharpe than 60/40: **88%**; of a smaller 10-year drawdown than 60/40: **80%**.
- Any single year: 39% chance of trailing 60/40, 13% chance of a loss. 1-year return 5th / 50th / 95th: -4.9% / +11.1% / +31.1%.

## 6. Synthetic shocks worse than history
Each shock is injected into the price data at several dates (a permanent level shift; prices then follow their real path) and the full model is rerun, so the model reacts as it would live. Loss = worst point from the day before the shock to 63 trading days after it ends. 'No-shock' is the same window without the shock. 60/40 is buy-and-hold from the day before.

### Crash day (1987-style, −20% equities and Bitcoin in one day)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -12.4% | 0.8% | -13.1 pp | -13.3% | tripped 2016-11-15 | 182 |
| 2017-09-15 | -12.4% | 0.1% | -12.4 pp | -14.1% | tripped 2017-09-15 | 570 |
| 2019-07-15 | -13.5% | -4.0% | -9.5 pp | -17.7% | tripped 2019-07-15 | 310 |
| 2021-06-15 | -15.1% | -1.5% | -13.7 pp | -17.2% | tripped 2021-06-15 | 612 |
| 2023-11-15 | -11.3% | -0.1% | -11.2 pp | -16.5% | tripped 2023-11-15 | 264 |
| 2025-08-15 | -14.4% | -1.7% | -12.7 pp | -18.3% | tripped 2025-08-15 | not yet |

Average loss: C&S -13.2% vs 60/40 -16.2% (C&S took 81% of 60/40's loss). Worst: C&S -15.1%, 60/40 -18.3%.

### Stocks and bonds fall together (equities −25%, bonds −15% over 6 months)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -2.1% | 0.8% | -2.8 pp | -16.2% | no | 28 |
| 2017-09-15 | -1.4% | 0.1% | -1.5 pp | -20.1% | no | 12 |
| 2019-07-15 | -10.6% | -6.7% | -3.9 pp | -35.4% | no | 194 |
| 2021-06-15 | -9.3% | -1.5% | -7.8 pp | -24.5% | no | 360 |
| 2023-11-15 | -3.6% | -0.1% | -3.5 pp | -13.4% | no | 53 |
| 2025-08-15 | -7.5% | -1.7% | -5.8 pp | -24.1% | no | 208 |

Average loss: C&S -5.7% vs 60/40 -22.3% (C&S took 26% of 60/40's loss). Worst: C&S -10.6%, 60/40 -35.4%.

### Stagflation (equities −20%, AGG/IGOV −10%, TIPS +3%, DBC +25% over 6 months)

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2016-11-15 | -1.6% | 0.8% | -2.4 pp | -10.8% | no | 9 |
| 2017-09-15 | -2.1% | 0.1% | -2.2 pp | -15.0% | no | 4 |
| 2019-07-15 | -9.5% | -6.7% | -2.8 pp | -31.2% | no | 184 |
| 2021-06-15 | -5.1% | -1.5% | -3.6 pp | -19.6% | no | 319 |
| 2023-11-15 | -7.0% | -0.1% | -6.9 pp | -8.2% | no | 64 |
| 2025-08-15 | -4.2% | -1.7% | -2.5 pp | -19.2% | no | 71 |

Average loss: C&S -4.9% vs 60/40 -17.3% (C&S took 28% of 60/40's loss). Worst: C&S -9.5%, 60/40 -31.2%.

### Bitcoin −80% in a month while the Bitcoin ETF is held

| Start | C&S loss | No-shock loss | Shock's own effect | 60/40 loss | Breaker | Back to pre-shock value (trading days after the low) |
|---|---|---|---|---|---|---|
| 2015-08-10 | -10.1% | -6.6% | -3.6 pp | -6.6% | no | 324 |
| 2016-11-08 | -4.1% | -0.8% | -3.3 pp | 0.3% | no | 29 |
| 2018-02-08 | -3.3% | -1.9% | -1.4 pp | -2.8% | no | 11 |
| 2020-09-09 | -3.7% | -1.1% | -2.7 pp | -2.1% | no | 12 |
| 2023-06-08 | -3.1% | 0.5% | -3.6 pp | -1.2% | no | 30 |
| 2025-03-10 | -8.0% | -4.7% | -3.3 pp | -11.6% | no | 70 |

Average extra loss from the Bitcoin crash: -3.0 pp (worst -3.6 pp). 60/40 isn't exposed, so it isn't a fair comparison here.

