# RAAM Backtest Report

Generated 2026-09-23 by `backtest/backtest.py`. Costs: 5 bps per side on turnover.
Engine: the live `scripts/raam.py compute_signal()` with `config/raam.json` (**Tier 1: BIL cash, cash-momentum hurdle, −20% breaker with auto re-entry**).
Signal at the month-end close, fill at the next open. The breaker is simulated on the daily path.
Data: Yahoo Finance adjusted daily OHLC. Past results do not guarantee future results.

## 1. Headline: Scenario A, real data only (2009-07-01 → 2026-09-23)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Worst month % | Down capture % | Up capture % | Months |
|---|---|---|---|---|---|---|---|---|
| RAAM live (Tier 1) — full | 4.07 | 6.19 | 0.68 | -12.75 | -5.41 | 30.32 | 28.81 | 207 |
| RAAM live (Tier 1) — 2009-2019 | 3.60 | 5.64 | 0.66 | -10.32 | -4.68 | 28.39 | 26.41 | 126 |
| RAAM live (Tier 1) — 2020-now | 4.80 | 7.00 | 0.71 | -7.46 | -5.41 | 32.45 | 31.89 | 81 |
| RAAM v1 original — full | 4.03 | 6.30 | 0.66 | -11.77 | -5.41 | 31.70 | 29.35 | 207 |
| RAAM v1 original — 2009-2019 | 3.77 | 5.66 | 0.68 | -10.17 | -4.68 | 27.30 | 26.57 | 126 |
| RAAM v1 original — 2020-now | 4.43 | 7.21 | 0.64 | -9.71 | -5.41 | 36.54 | 32.90 | 81 |
| SPY — full | 15.08 | 14.79 | 1.03 | -23.31 | -16.35 |  |  | 207 |
| SPY — 2009-2019 | 14.96 | 13.05 | 1.14 | -17.10 | -11.73 |  |  | 126 |
| SPY — 2020-now | 15.27 | 17.22 | 0.92 | -23.31 | -16.35 |  |  | 81 |
| Equal-weight 7Twelve — full | 7.64 | 10.76 | 0.74 | -20.18 | -14.34 | 69.82 | 60.46 | 207 |
| Equal-weight 7Twelve — 2009-2019 | 7.85 | 9.74 | 0.83 | -15.27 | -9.27 | 71.80 | 61.79 | 126 |
| Equal-weight 7Twelve — 2020-now | 7.31 | 12.25 | 0.64 | -18.25 | -14.34 | 67.65 | 58.74 | 81 |

The Sharpe uses rf = 0.
- **Down capture:** the average RAAM return in SPY's down months, as a % of SPY's loss. Lower is better defence.
- **Up capture:** the same, for SPY's up months.

**Live config, daily path:**
- Max drawdown **-16.2%** on 2020-03-18. SPY's max drawdown over the same span was -33.7%.
- Worst day **-3.0%**.
- Breaker trips: **0** 

## 2. Pre-registered variants (Scenario A, full period)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (daily) | Down capture % | Up capture % | Turnover/yr | Avg cash % | Breaker trips |
|---|---|---|---|---|---|---|---|---|---|
| v1 original (SHY, 0% hurdle, no breaker) | 4.03 | 6.30 | 0.66 | -15.34 | 31.70 | 29.35 | 7.67 | 22.71 | 0 |
| + BIL as cash only | 4.16 | 6.26 | 0.68 | -15.81 | 31.12 | 29.52 | 7.67 | 22.71 | 0 |
| + cash hurdle only (SHY) | 3.94 | 6.17 | 0.66 | -15.60 | 30.66 | 28.54 | 7.76 | 25.80 | 0 |
| Tier 1 signals (BIL + cash hurdle) | 4.07 | 6.19 | 0.68 | -16.15 | 30.32 | 28.81 | 7.78 | 25.31 | 0 |
| Tier 1 + breaker -15% auto | 3.84 | 6.31 | 0.63 | -16.39 | 31.93 | 28.81 | 7.80 | 25.31 | 1 |
| **LIVE: Tier 1 + breaker -20% auto** | 4.07 | 6.19 | 0.68 | -16.15 | 30.32 | 28.81 | 7.78 | 25.31 | 0 |
| Live + no ATR trend filter | 4.72 | 5.74 | 0.83 | -12.00 | 24.27 | 28.11 | 7.11 | 27.44 | 0 |
| Live + A3 lower band literal | 4.60 | 5.79 | 0.81 | -12.00 | 24.48 | 27.79 | 7.25 | 27.34 | 0 |
| Live + momentum-heavy 50/25/25 | 5.60 | 7.88 | 0.73 | -17.32 | 39.33 | 38.56 | 8.43 | 18.65 | 0 |

### The same variants, out-of-sample only (2020 → now)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Down capture % | Up capture % |
|---|---|---|---|---|---|---|
| v1 original (SHY, 0% hurdle, no breaker) | 4.43 | 7.21 | 0.64 | -9.71 | 36.54 | 32.90 |
| + BIL as cash only | 5.02 | 7.13 | 0.72 | -7.50 | 34.26 | 33.48 |
| + cash hurdle only (SHY) | 3.90 | 7.06 | 0.58 | -10.75 | 35.61 | 30.79 |
| Tier 1 signals (BIL + cash hurdle) | 4.80 | 7.00 | 0.71 | -7.46 | 32.45 | 31.89 |
| Tier 1 + breaker -15% auto | 4.21 | 7.27 | 0.60 | -7.46 | 35.83 | 31.88 |
| **LIVE: Tier 1 + breaker -20% auto** | 4.80 | 7.00 | 0.71 | -7.46 | 32.45 | 31.89 |
| Live + no ATR trend filter | 6.52 | 6.05 | 1.08 | -6.19 | 22.09 | 31.59 |
| Live + A3 lower band literal | 6.32 | 6.07 | 1.04 | -6.83 | 22.51 | 31.22 |
| Live + momentum-heavy 50/25/25 | 5.84 | 8.16 | 0.74 | -10.75 | 35.67 | 36.90 |

## 3. 2008 stress test: Scenario B, with IGOV spliced from BWX (entries Jun-2008 → Jun-2009)
| Variant | CAGR % | Vol % | MaxDD % (monthly) | Worst month % | Total % | Months |
|---|---|---|---|---|---|---|
| RAAM live (Tier 1) | 0.98 | 9.44 | -9.63 | -3.36 | 1.06 | 13 |
| RAAM v1 original | 3.54 | 9.59 | -7.33 | -3.25 | 3.84 | 13 |
| SPY | -29.80 | 31.15 | -43.45 | -16.04 | -31.84 | 13 |
| Equal-weight 7Twelve | -22.44 | 28.54 | -37.43 | -16.35 | -24.07 | 13 |

Scenario B live-config breaker trips: none.

## 4. Calendar years (Scenario A)
| Year | RAAM live % | RAAM v1 % | SPY % | EW 7Twelve % | Live avg cash % |
|---|---|---|---|---|---|
| 2009 | 10.5 | 10.5 | 22.9 | 18.9 | 0 |
| 2010 | 11.0 | 11.4 | 15.0 | 14.3 | 13 |
| 2011 | 4.8 | 4.9 | 2.9 | 0.4 | 30 |
| 2012 | 4.4 | 4.5 | 16.1 | 11.9 | 13 |
| 2013 | 2.0 | 2.2 | 29.3 | 8.3 | 40 |
| 2014 | 3.0 | 3.2 | 14.4 | 2.8 | 10 |
| 2015 | -5.2 | -4.9 | -0.8 | -5.9 | 45 |
| 2016 | -2.0 | -2.2 | 14.7 | 12.1 | 22 |
| 2017 | 10.9 | 11.0 | 21.3 | 13.3 | 10 |
| 2018 | -2.8 | -2.0 | -6.4 | -8.2 | 45 |
| 2019 | 2.6 | 2.6 | 34.0 | 18.6 | 15 |
| 2020 | 6.0 | 6.9 | 18.2 | 9.8 | 22 |
| 2021 | 14.8 | 14.6 | 28.6 | 14.7 | 18 |
| 2022 | -1.5 | -6.6 | -18.0 | -12.3 | 72 |
| 2023 | -2.0 | -0.6 | 24.7 | 9.6 | 35 |
| 2024 | -1.1 | -1.0 | 26.4 | 6.9 | 8 |
| 2025 | 6.1 | 7.4 | 17.7 | 12.5 | 17 |
| 2026 | 11.4 | 10.8 | 12.8 | 10.7 | 29 |

## 5. How often each ETF was held, live config (% of months)
AGG 63.8% · TIP 62.8% · BIL 56% · IGOV 42.5% · RWR 41.1% · DBC 39.1% · VV 33.3% · IJR 25.6% · EFA 17.9% · VAW 17.4% · EEM 15.5% · IJH 14.5%

![equity](equity_curve.png)
