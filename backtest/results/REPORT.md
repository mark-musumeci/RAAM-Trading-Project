# RAAM Backtest Report

Generated 2026-09-23 by `backtest/backtest.py`. Costs: 5 bps per side on turnover.
Engine: the live `scripts/raam.py compute_signal()` with `config/raam.json` (**Core & Shield: fixed Core of 30% SPY + 20% AGG, plus 50% RAAM Shield with Tier 1 rules and the trend term off; −20% breaker on the whole portfolio**).
Signal at the month-end close, fill at the next open. The breaker is simulated on the daily path.
Data: Yahoo Finance adjusted daily OHLC. Past results do not guarantee future results.

## 1. Headline: Scenario A, real data only (2009-07-01 → 2026-09-23)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Worst month % | Down capture % | Up capture % | Months |
|---|---|---|---|---|---|---|---|---|
| Core & Shield (live) — full | 7.49 | 6.75 | 1.11 | -11.06 | -5.66 | 42.66 | 46.07 | 207 |
| Core & Shield (live) — 2009-2019 | 7.11 | 5.93 | 1.19 | -7.14 | -4.87 | 39.89 | 44.17 | 126 |
| Core & Shield (live) — 2020-now | 8.08 | 7.89 | 1.03 | -11.06 | -5.66 | 45.70 | 48.51 | 81 |
| Shield alone (RAAM) — full | 4.72 | 5.74 | 0.83 | -10.39 | -4.68 | 24.27 | 28.11 | 207 |
| Shield alone (RAAM) — 2009-2019 | 3.59 | 5.54 | 0.66 | -10.39 | -4.68 | 26.25 | 25.40 | 126 |
| Shield alone (RAAM) — 2020-now | 6.52 | 6.05 | 1.08 | -6.19 | -4.45 | 22.09 | 31.59 | 81 |
| 60/40 — full | 10.18 | 9.31 | 1.09 | -19.24 | -10.04 | 61.02 | 64.08 | 207 |
| 60/40 — 2009-2019 | 10.65 | 7.67 | 1.36 | -8.70 | -6.24 | 53.51 | 63.00 | 126 |
| 60/40 — 2020-now | 9.44 | 11.46 | 0.85 | -19.24 | -10.04 | 69.30 | 65.47 | 81 |
| 30/70 — full | 6.38 | 5.75 | 1.11 | -16.27 | -5.30 | 31.79 | 37.14 | 207 |
| 30/70 — 2009-2019 | 7.29 | 4.04 | 1.77 | -3.22 | -2.59 | 18.64 | 35.25 | 126 |
| 30/70 — 2020-now | 4.98 | 7.71 | 0.67 | -16.27 | -5.30 | 46.28 | 39.57 | 81 |
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
- Max drawdown **-14.6%** on 2020-03-18. SPY's max drawdown over the same span was -33.7%.
- Worst day **-4.2%**.
- Breaker trips: **0** 

## 2. Pre-registered variants (Scenario A, full period)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (daily) | Down capture % | Up capture % | Turnover/yr | Avg cash % | Breaker trips |
|---|---|---|---|---|---|---|---|---|---|
| **LIVE: Core & Shield (50% 60/40 + 50% RAAM)** | 7.49 | 6.75 | 1.11 | -14.61 | 42.66 | 46.07 | 3.69 | 13.72 | 0 |
| Shield alone (RAAM, live rules) | 4.72 | 5.74 | 0.83 | -12.00 | 24.27 | 28.11 | 7.11 | 27.44 | 0 |
| RAAM alone, original paper rules (v1) | 4.03 | 6.30 | 0.66 | -15.34 | 31.70 | 29.35 | 7.67 | 22.71 | 0 |
| Core & Shield 70/30 (42% SPY, 28% AGG, 30% RAAM) | 8.44 | 7.78 | 1.08 | -15.36 | 50.82 | 53.25 | 2.39 | 8.23 | 1 |
| Core & Shield 30/70 (18% SPY, 12% AGG, 70% RAAM) | 6.39 | 6.09 | 1.05 | -12.17 | 35.30 | 38.89 | 5.06 | 19.21 | 0 |
| Core & Shield with trend filter on | 7.16 | 6.91 | 1.04 | -15.91 | 45.68 | 46.43 | 4.02 | 12.66 | 0 |
| Core & Shield, SHY as cash | 7.43 | 6.75 | 1.10 | -14.07 | 42.81 | 45.97 | 3.64 | 13.77 | 0 |

### The same variants, out-of-sample only (2020 → now)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Down capture % | Up capture % |
|---|---|---|---|---|---|---|
| **LIVE: Core & Shield (50% 60/40 + 50% RAAM)** | 8.08 | 7.89 | 1.03 | -11.06 | 45.70 | 48.51 |
| Shield alone (RAAM, live rules) | 6.52 | 6.05 | 1.08 | -6.19 | 22.09 | 31.59 |
| RAAM alone, original paper rules (v1) | 4.43 | 7.21 | 0.64 | -9.71 | 36.54 | 32.90 |
| Core & Shield 70/30 (42% SPY, 28% AGG, 30% RAAM) | 8.31 | 9.46 | 0.89 | -14.39 | 56.86 | 55.25 |
| Core & Shield 30/70 (18% SPY, 12% AGG, 70% RAAM) | 7.48 | 6.83 | 1.09 | -7.92 | 36.26 | 41.74 |
| Core & Shield with trend filter on | 7.22 | 8.18 | 0.90 | -11.60 | 50.89 | 48.66 |
| Core & Shield, SHY as cash | 7.60 | 7.93 | 0.97 | -12.98 | 47.29 | 47.93 |

## 3. 2008 stress test: Scenario B, with IGOV spliced from BWX (entries Jun-2008 → Jun-2009)
| Variant | CAGR % | Vol % | MaxDD % (monthly) | Worst month % | Total % | Months |
|---|---|---|---|---|---|---|
| Core & Shield (live) | -6.85 | 12.86 | -17.35 | -5.42 | -7.40 | 13 |
| Shield alone (RAAM) | 1.48 | 9.91 | -9.63 | -3.36 | 1.60 | 13 |
| 60/40 | -16.48 | 19.94 | -27.57 | -10.24 | -17.72 | 13 |
| SPY | -29.80 | 31.15 | -43.45 | -16.04 | -31.84 | 13 |
| Equal-weight 7Twelve | -22.44 | 28.54 | -37.43 | -16.35 | -24.07 | 13 |

Scenario B live-config breaker trips: [('2009-02-23', -20.2, -0.9)].

## 4. Calendar years (Scenario A)
| Year | Core & Shield % | Shield alone % | 60/40 % | SPY % | EW 7Twelve % | C&S avg cash % |
|---|---|---|---|---|---|---|
| 2009 | 13.4 | 12.0 | 14.9 | 22.9 | 18.9 | 0 |
| 2010 | 10.8 | 9.7 | 11.9 | 15.0 | 14.3 | 7 |
| 2011 | 5.1 | 4.9 | 5.3 | 2.9 | 0.4 | 15 |
| 2012 | 7.7 | 4.4 | 11.1 | 16.1 | 11.9 | 7 |
| 2013 | 8.9 | 2.0 | 16.0 | 29.3 | 8.3 | 20 |
| 2014 | 8.0 | 5.0 | 11.0 | 14.4 | 2.8 | 8 |
| 2015 | -2.5 | -5.1 | -0.0 | -0.8 | -5.9 | 23 |
| 2016 | 3.7 | -2.0 | 9.6 | 14.7 | 12.1 | 11 |
| 2017 | 11.8 | 9.6 | 14.1 | 21.3 | 13.3 | 8 |
| 2018 | -3.8 | -4.4 | -3.3 | -6.4 | -8.2 | 25 |
| 2019 | 12.9 | 3.0 | 23.7 | 34.0 | 18.6 | 8 |
| 2020 | 11.5 | 8.0 | 14.7 | 18.2 | 9.8 | 14 |
| 2021 | 16.1 | 16.6 | 15.6 | 28.6 | 14.7 | 9 |
| 2022 | -7.8 | -0.3 | -15.2 | -18.0 | -12.3 | 37 |
| 2023 | 6.7 | -2.2 | 16.2 | 24.7 | 9.6 | 18 |
| 2024 | 10.3 | 4.6 | 16.1 | 26.4 | 6.9 | 8 |
| 2025 | 11.1 | 8.7 | 13.5 | 17.7 | 12.5 | 8 |
| 2026 | 8.3 | 9.6 | 6.8 | 12.8 | 10.7 | 17 |

## 5. How often each ETF was held, live config (% of months; SPY and AGG are always held via the Core)
AGG 100% · SPY 100% · TIP 64.7% · BIL 61.4% · IGOV 44% · RWR 43% · DBC 39.1% · VV 31.4% · IJR 21.7% · EFA 15% · VAW 14.5% · EEM 13.5% · IJH 11.6%

![equity](equity_curve.png)
