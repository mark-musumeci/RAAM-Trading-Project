# RAAM Backtest Report

Generated 2026-10-15 by `backtest/backtest.py`. Costs: 5 bps per side on turnover.
Engine: the live `scripts/raam.py compute_signal()` with `config/raam.json` (**Core & Shield: Core = 50% QQQM while its month-end close is above its 10-month average, else T-bills (SGOV); QQQM before Oct 2020 = QQQ, the same index. Plus 50% RAAM Shield of 12 candidates incl. a spot Bitcoin ETF (BTC), capped at 5% of the portfolio; Tier 1 rules, trend term off, −20% breaker on the whole portfolio**).
BTC (Grayscale Bitcoin Mini Trust) before its Jul-2024 launch = BTC-USD aligned to US trading days minus its 0.15%/yr fee, spliced into the real fund. SGOV before May 2020 = BIL and SCHP before Aug 2010 = TIP (same exposures). All rows share the live config's window.
Signal at the month-end close, fill at the next open. The breaker is simulated on the daily path.
Data: Yahoo Finance adjusted daily OHLC. Past results do not guarantee future results.

## 1. Headline: common window (2015-02-02 → 2026-09-25)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Worst month % | Down capture % | Up capture % | Months |
|---|---|---|---|---|---|---|---|---|
| Core & Shield (live) — full | 11.78 | 9.73 | 1.20 | -11.72 | -8.78 | 45.68 | 63.24 | 140 |
| Core & Shield (live) — to 2019 | 10.26 | 8.32 | 1.22 | -8.76 | -6.22 | 48.52 | 65.10 | 59 |
| Core & Shield (live) — 2020-now | 12.90 | 10.68 | 1.19 | -11.72 | -8.78 | 44.23 | 62.22 | 81 |
| Shield alone (RAAM) — full | 8.93 | 8.28 | 1.08 | -10.68 | -4.44 | 18.89 | 40.46 | 140 |
| Shield alone (RAAM) — to 2019 | 9.87 | 9.04 | 1.09 | -10.68 | -3.45 | 12.75 | 46.93 | 59 |
| Shield alone (RAAM) — 2020-now | 8.25 | 7.73 | 1.07 | -6.61 | -4.44 | 22.05 | 36.92 | 81 |
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
- Worst day **-5.3%**.
- Breaker trips: **1** [('2020-03-12', -15.3, -5.2)]

## 2. Pre-registered variants (Scenario A, full period)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (daily) | Down capture % | Up capture % | Turnover/yr | Avg cash % | Breaker trips |
|---|---|---|---|---|---|---|---|---|---|
| **LIVE: QQQM trend Core + Shield (Bitcoin capped 5%)** | 11.78 | 9.73 | 1.20 | -15.43 | 45.68 | 63.24 | 5.14 | 25.68 | 1 |
| Previous live: fixed 60/40 Core (30% SPY + 20% AGG) | 9.17 | 7.78 | 1.17 | -14.08 | 41.76 | 52.38 | 3.72 | 16.39 | 0 |
| QQQM Core without the trend filter | 13.71 | 11.96 | 1.14 | -24.53 | 65.29 | 79.79 | 3.91 | 16.39 | 2 |
| Live rules WITHOUT Bitcoin | 8.89 | 8.98 | 1.00 | -16.14 | 47.79 | 54.81 | 5.26 | 24.71 | 1 |
| Core & Shield + Bitcoin uncapped (10% slots) | 15.26 | 11.63 | 1.29 | -16.00 | 45.77 | 74.78 | 5.27 | 23.07 | 1 |
| Shield alone (RAAM, live rules) | 8.93 | 8.28 | 1.08 | -14.68 | 18.89 | 40.46 | 7.15 | 32.79 | 0 |
| RAAM alone, original paper rules (v1, no Bitcoin) | 2.74 | 6.18 | 0.47 | -15.25 | 32.14 | 25.95 | 8.08 | 24.14 | 0 |
| Core & Shield 70/30 (42% SPY, 28% AGG, 30% RAAM) | 10.37 | 9.18 | 1.13 | -15.91 | 52.09 | 61.74 | 2.52 | 8.79 | 1 |
| Core & Shield 30/70 (18% SPY, 12% AGG, 70% RAAM) | 7.75 | 6.77 | 1.14 | -11.16 | 32.58 | 43.00 | 5.04 | 23.99 | 0 |
| Core & Shield with trend filter on | 11.34 | 10.03 | 1.13 | -15.43 | 49.71 | 63.93 | 5.68 | 24.43 | 1 |
| Core & Shield, SHY as cash | 11.30 | 9.85 | 1.14 | -16.96 | 47.95 | 62.89 | 5.12 | 25.36 | 1 |
| Bitcoin flattened to 0%/yr (hindsight check) | 9.79 | 9.35 | 1.05 | -16.14 | 47.27 | 57.56 | 5.17 | 25.79 | 1 |

### The same variants, out-of-sample only (2020 → now)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Down capture % | Up capture % |
|---|---|---|---|---|---|---|
| **LIVE: QQQM trend Core + Shield (Bitcoin capped 5%)** | 12.90 | 10.68 | 1.19 | -11.72 | 44.23 | 62.22 |
| Previous live: fixed 60/40 Core (30% SPY + 20% AGG) | 8.98 | 8.46 | 1.06 | -11.02 | 45.68 | 51.14 |
| QQQM Core without the trend filter | 13.48 | 13.13 | 1.03 | -22.66 | 68.35 | 76.89 |
| Live rules WITHOUT Bitcoin | 11.93 | 9.94 | 1.19 | -12.29 | 44.27 | 59.27 |
| Core & Shield + Bitcoin uncapped (10% slots) | 14.87 | 12.22 | 1.20 | -12.07 | 45.27 | 68.71 |
| Shield alone (RAAM, live rules) | 8.25 | 7.73 | 1.07 | -6.61 | 22.05 | 36.92 |
| RAAM alone, original paper rules (v1, no Bitcoin) | 4.51 | 7.20 | 0.65 | -9.69 | 36.45 | 33.02 |
| Core & Shield 70/30 (42% SPY, 28% AGG, 30% RAAM) | 9.64 | 10.18 | 0.96 | -14.36 | 57.29 | 59.40 |
| Core & Shield 30/70 (18% SPY, 12% AGG, 70% RAAM) | 7.94 | 7.22 | 1.10 | -7.87 | 35.81 | 42.86 |
| Core & Shield with trend filter on | 12.18 | 11.00 | 1.10 | -11.72 | 49.53 | 62.98 |
| Core & Shield, SHY as cash | 11.88 | 10.91 | 1.09 | -12.64 | 48.78 | 61.71 |
| Bitcoin flattened to 0%/yr (hindsight check) | 11.40 | 10.20 | 1.11 | -12.29 | 44.74 | 58.10 |

## 3. 2008 stress test: Scenario B, IGOV spliced from BWX (entries Jun-2008 → Jun-2009). Bitcoin did not exist, so the rows run the rules WITHOUT Bitcoin
| Variant | CAGR % | Vol % | MaxDD % (monthly) | Worst month % | Total % | Months |
|---|---|---|---|---|---|---|
| Core & Shield (no Bitcoin) | -0.73 | 7.75 | -4.61 | -4.47 | -0.79 | 13 |
| Shield alone (RAAM) | 1.48 | 9.91 | -9.63 | -3.36 | 1.60 | 13 |
| 60/40 | -16.48 | 19.94 | -27.57 | -10.24 | -17.72 | 13 |
| SPY | -29.80 | 31.15 | -43.45 | -16.04 | -31.84 | 13 |
| Equal-weight 7Twelve | -22.44 | 28.54 | -37.43 | -16.35 | -24.07 | 13 |

Scenario B live-config breaker trips: [('2020-03-12', -16.0, -5.2)].

## 4. Calendar years (Scenario A)
| Year | Core & Shield % | Shield alone % | 60/40 % | SPY % | EW 7Twelve % | C&S avg cash % |
|---|---|---|---|---|---|---|
| 2015 | -1.9 | -1.5 | 1.1 | 2.3 | -5.7 | 31 |
| 2016 | 4.5 | 8.0 | 9.6 | 14.7 | 12.1 | 26 |
| 2017 | 38.9 | 45.1 | 14.1 | 21.3 | 13.3 | 12 |
| 2018 | -0.8 | -10.7 | -3.3 | -6.4 | -8.2 | 34 |
| 2019 | 14.6 | 15.2 | 23.7 | 34.0 | 18.6 | 21 |
| 2020 | 18.7 | 15.8 | 14.7 | 18.2 | 9.8 | 20 |
| 2021 | 22.0 | 16.7 | 15.6 | 28.6 | 14.7 | 11 |
| 2022 | -4.7 | -2.3 | -15.2 | -18.0 | -12.3 | 83 |
| 2023 | 19.4 | 1.8 | 16.2 | 24.7 | 9.6 | 23 |
| 2024 | 18.3 | 9.4 | 16.1 | 26.4 | 6.9 | 9 |
| 2025 | 9.0 | 7.6 | 13.5 | 17.7 | 12.5 | 16 |
| 2026 | 6.8 | 8.1 | 7.0 | 13.4 | 10.7 | 22 |

## 5. How often each ETF was held, live config (% of months; QQQM counts the months the Core trend filter was on)
SGOV 88.6% · QQQM 81.4% · SCHP 60% · AGG 55% · BTC 52.1% · DBC 40% · IGOV 36.4% · VV 32.9% · RWR 32.1% · IJR 14.3% · EEM 13.6% · VAW 10.7% · EFA 10.7% · IJH 4.3%

![equity](equity_curve.png)
