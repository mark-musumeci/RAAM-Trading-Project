# RAAM Backtest Report

Generated 2026-10-14 by `backtest/backtest.py`. Costs: 5 bps per side on turnover.
Engine: the live `scripts/raam.py compute_signal()` with `config/raam.json` (**Core & Shield: Core = 50% QQQM while its month-end close is above its 10-month average, else T-bills (BIL); QQQM before Oct 2020 = QQQ, the same index. Plus 50% RAAM Shield of 12 candidates incl. IBIT, capped at 5% of the portfolio; Tier 1 rules, trend term off, −20% breaker on the whole portfolio**).
IBIT before its Jan-2024 launch = BTC-USD aligned to US trading days minus a 0.25%/yr fee, spliced into real IBIT. All rows share the live config's window.
Signal at the month-end close, fill at the next open. The breaker is simulated on the daily path.
Data: Yahoo Finance adjusted daily OHLC. Past results do not guarantee future results.

## 1. Headline: common window (2015-02-02 → 2026-09-25)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Worst month % | Down capture % | Up capture % | Months |
|---|---|---|---|---|---|---|---|---|
| Core & Shield (live) — full | 11.90 | 9.74 | 1.21 | -11.67 | -8.73 | 45.54 | 63.53 | 140 |
| Core & Shield (live) — to 2019 | 10.27 | 8.32 | 1.22 | -8.76 | -6.22 | 48.53 | 65.14 | 59 |
| Core & Shield (live) — 2020-now | 13.10 | 10.69 | 1.21 | -11.67 | -8.73 | 44.01 | 62.65 | 81 |
| Shield alone (RAAM) — full | 9.16 | 8.32 | 1.10 | -10.69 | -4.45 | 18.65 | 41.11 | 140 |
| Shield alone (RAAM) — to 2019 | 9.89 | 9.04 | 1.09 | -10.69 | -3.45 | 12.76 | 46.99 | 59 |
| Shield alone (RAAM) — 2020-now | 8.64 | 7.81 | 1.10 | -6.72 | -4.45 | 21.68 | 37.88 | 81 |
| 60/40 — full | 9.16 | 10.02 | 0.93 | -19.24 | -10.04 | 64.62 | 64.34 | 140 |
| 60/40 — to 2019 | 8.75 | 7.72 | 1.13 | -8.45 | -6.24 | 55.52 | 62.42 | 59 |
| 60/40 — 2020-now | 9.47 | 11.46 | 0.85 | -19.24 | -10.04 | 69.30 | 65.40 | 81 |
| 30/70 — full | 5.31 | 6.43 | 0.84 | -16.27 | -5.30 | 38.09 | 37.60 | 140 |
| 30/70 — to 2019 | 5.78 | 4.12 | 1.39 | -3.22 | -2.59 | 22.15 | 34.24 | 59 |
| 30/70 — 2020-now | 4.96 | 7.71 | 0.67 | -16.27 | -5.30 | 46.28 | 39.45 | 81 |
| SPY — full | 14.14 | 15.57 | 0.93 | -23.31 | -16.35 |  |  | 140 |
| SPY — to 2019 | 12.50 | 13.08 | 0.97 | -15.30 | -11.73 |  |  | 59 |
| SPY — 2020-now | 15.35 | 17.22 | 0.92 | -23.31 | -16.35 |  |  | 81 |
| Equal-weight 7Twelve — full | 6.56 | 10.75 | 0.65 | -20.18 | -14.34 | 66.53 | 57.09 | 140 |
| Equal-weight 7Twelve — to 2019 | 5.55 | 8.35 | 0.69 | -11.12 | -6.53 | 64.35 | 54.32 | 59 |
| Equal-weight 7Twelve — 2020-now | 7.31 | 12.25 | 0.64 | -18.25 | -14.34 | 67.65 | 58.61 | 81 |

The Sharpe uses rf = 0.
- **Down capture:** the average RAAM return in SPY's down months, as a % of SPY's loss. Lower is better defence.
- **Up capture:** the same, for SPY's up months.

**Live config, daily path:**
- Max drawdown **-15.4%** on 2020-04-01. SPY's max drawdown over the same span was -33.7%.
- Worst day **-5.2%**.
- Breaker trips: **1** [('2020-03-12', -15.3, -5.1)]

## 2. Pre-registered variants (Scenario A, full period)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (daily) | Down capture % | Up capture % | Turnover/yr | Avg cash % | Breaker trips |
|---|---|---|---|---|---|---|---|---|---|
| **LIVE: QQQM trend Core + Shield (IBIT capped 5%)** | 11.90 | 9.74 | 1.21 | -15.39 | 45.54 | 63.53 | 5.12 | 25.75 | 1 |
| Previous live: fixed 60/40 Core (30% SPY + 20% AGG) | 9.28 | 7.82 | 1.18 | -14.11 | 41.64 | 52.70 | 3.70 | 16.46 | 0 |
| QQQM Core without the trend filter | 13.84 | 12.00 | 1.14 | -24.60 | 65.15 | 80.11 | 3.89 | 16.46 | 2 |
| Live rules WITHOUT IBIT | 9.03 | 9.00 | 1.01 | -16.09 | 47.61 | 55.19 | 5.23 | 24.64 | 1 |
| Core & Shield + IBIT uncapped (10% slots) | 15.38 | 11.67 | 1.29 | -15.96 | 45.74 | 75.15 | 5.25 | 23.14 | 1 |
| Shield alone (RAAM, live rules) | 9.16 | 8.32 | 1.10 | -14.71 | 18.65 | 41.11 | 7.12 | 32.93 | 0 |
| RAAM alone, original paper rules (v1, no IBIT) | 2.79 | 6.19 | 0.48 | -15.34 | 31.91 | 26.01 | 7.95 | 24.14 | 0 |
| Core & Shield 70/30 (42% SPY, 28% AGG, 30% RAAM) | 10.44 | 9.20 | 1.13 | -15.95 | 52.05 | 61.97 | 2.51 | 8.84 | 1 |
| Core & Shield 30/70 (18% SPY, 12% AGG, 70% RAAM) | 7.91 | 6.81 | 1.15 | -11.21 | 32.37 | 43.42 | 5.02 | 24.09 | 0 |
| Core & Shield with trend filter on | 11.51 | 10.02 | 1.14 | -15.39 | 49.86 | 64.54 | 5.69 | 24.50 | 1 |
| Core & Shield, SHY as cash | 11.36 | 9.87 | 1.14 | -17.01 | 47.95 | 63.09 | 5.12 | 25.50 | 1 |
| IBIT flattened to 0%/yr (hindsight check) | 10.16 | 9.44 | 1.08 | -16.07 | 47.12 | 58.71 | 5.17 | 25.71 | 1 |

### The same variants, out-of-sample only (2020 → now)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Down capture % | Up capture % |
|---|---|---|---|---|---|---|
| **LIVE: QQQM trend Core + Shield (IBIT capped 5%)** | 13.10 | 10.69 | 1.21 | -11.67 | 44.01 | 62.65 |
| Previous live: fixed 60/40 Core (30% SPY + 20% AGG) | 9.17 | 8.51 | 1.08 | -11.06 | 45.50 | 51.63 |
| QQQM Core without the trend filter | 13.68 | 13.21 | 1.04 | -22.72 | 68.12 | 77.37 |
| Live rules WITHOUT IBIT | 12.03 | 9.93 | 1.20 | -12.24 | 44.21 | 59.52 |
| Core & Shield + IBIT uncapped (10% slots) | 15.07 | 12.29 | 1.21 | -12.01 | 45.21 | 69.28 |
| Shield alone (RAAM, live rules) | 8.64 | 7.81 | 1.10 | -6.72 | 21.68 | 37.88 |
| RAAM alone, original paper rules (v1, no IBIT) | 4.47 | 7.20 | 0.64 | -9.71 | 36.54 | 32.95 |
| Core & Shield 70/30 (42% SPY, 28% AGG, 30% RAAM) | 9.77 | 10.22 | 0.97 | -14.39 | 57.22 | 59.74 |
| Core & Shield 30/70 (18% SPY, 12% AGG, 70% RAAM) | 8.21 | 7.28 | 1.12 | -7.92 | 35.49 | 43.48 |
| Core & Shield with trend filter on | 12.24 | 11.00 | 1.11 | -11.66 | 49.75 | 63.25 |
| Core & Shield, SHY as cash | 11.96 | 10.93 | 1.09 | -12.69 | 48.78 | 61.94 |
| IBIT flattened to 0%/yr (hindsight check) | 12.04 | 10.33 | 1.16 | -12.24 | 44.54 | 59.84 |

## 3. 2008 stress test: Scenario B, IGOV spliced from BWX (entries Jun-2008 → Jun-2009). Bitcoin did not exist, so the rows run the rules WITHOUT IBIT
| Variant | CAGR % | Vol % | MaxDD % (monthly) | Worst month % | Total % | Months |
|---|---|---|---|---|---|---|
| Core & Shield (no IBIT) | -0.73 | 7.75 | -4.61 | -4.47 | -0.79 | 13 |
| Shield alone (RAAM) | 1.48 | 9.91 | -9.63 | -3.36 | 1.60 | 13 |
| 60/40 | -16.48 | 19.94 | -27.57 | -10.24 | -17.72 | 13 |
| SPY | -29.80 | 31.15 | -43.45 | -16.04 | -31.84 | 13 |
| Equal-weight 7Twelve | -22.44 | 28.54 | -37.43 | -16.35 | -24.07 | 13 |

Scenario B live-config breaker trips: [('2020-03-12', -15.9, -5.1)].

## 4. Calendar years (Scenario A)
| Year | Core & Shield % | Shield alone % | 60/40 % | SPY % | EW 7Twelve % | C&S avg cash % |
|---|---|---|---|---|---|---|
| 2015 | -1.9 | -1.5 | 1.1 | 2.3 | -5.7 | 31 |
| 2016 | 4.5 | 8.1 | 9.6 | 14.7 | 12.1 | 26 |
| 2017 | 38.8 | 45.1 | 14.1 | 21.3 | 13.3 | 12 |
| 2018 | -0.8 | -10.7 | -3.3 | -6.4 | -8.2 | 34 |
| 2019 | 14.6 | 15.2 | 23.7 | 34.0 | 18.6 | 21 |
| 2020 | 18.6 | 15.5 | 14.7 | 18.2 | 9.8 | 20 |
| 2021 | 21.9 | 16.5 | 15.6 | 28.6 | 14.7 | 11 |
| 2022 | -4.9 | -2.5 | -15.2 | -18.0 | -12.3 | 83 |
| 2023 | 19.3 | 1.7 | 16.2 | 24.7 | 9.6 | 23 |
| 2024 | 19.1 | 10.9 | 16.1 | 26.4 | 6.9 | 10 |
| 2025 | 8.9 | 7.5 | 13.5 | 17.7 | 12.5 | 16 |
| 2026 | 7.7 | 10.0 | 7.0 | 13.4 | 10.7 | 22 |

## 5. How often each ETF was held, live config (% of months; SPY and AGG are always held via the Core)
BIL 88.6% · QQQM 81.4% · TIP 59.3% · AGG 55% · IBIT 52.1% · DBC 40.7% · IGOV 35.7% · RWR 33.6% · VV 33.6% · IJR 14.3% · EEM 12.9% · VAW 10% · EFA 10% · IJH 4.3%

![equity](equity_curve.png)
