# RAAM Backtest Report

Generated 2026-09-26 by `backtest/backtest.py`. Costs: 5 bps per side on turnover.
Engine: the live `scripts/raam.py compute_signal()` with `config/raam.json` (**Core & Shield: fixed Core of 30% SPY + 20% AGG, plus 50% RAAM Shield of 12 candidates incl. IBIT, capped at 5% of the portfolio; Tier 1 rules, trend term off, −20% breaker on the whole portfolio**).
IBIT before its Jan-2024 launch = BTC-USD aligned to US trading days minus a 0.25%/yr fee, spliced into real IBIT. All rows share the live config's window.
Signal at the month-end close, fill at the next open. The breaker is simulated on the daily path.
Data: Yahoo Finance adjusted daily OHLC. Past results do not guarantee future results.

## 1. Headline: common window (2015-02-02 → 2026-09-25)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Worst month % | Down capture % | Up capture % | Months |
|---|---|---|---|---|---|---|---|---|
| Core & Shield (live) — full | 9.28 | 7.82 | 1.18 | -11.06 | -5.65 | 41.64 | 52.70 | 140 |
| Core & Shield (live) — to 2019 | 9.43 | 6.82 | 1.36 | -7.14 | -4.07 | 34.14 | 54.67 | 59 |
| Core & Shield (live) — 2020-now | 9.17 | 8.51 | 1.08 | -11.06 | -5.65 | 45.50 | 51.63 | 81 |
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
- Max drawdown **-14.1%** on 2020-03-18. SPY's max drawdown over the same span was -33.7%.
- Worst day **-4.2%**.
- Breaker trips: **0** 

## 2. Pre-registered variants (Scenario A, full period)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (daily) | Down capture % | Up capture % | Turnover/yr | Avg cash % | Breaker trips |
|---|---|---|---|---|---|---|---|---|---|
| **LIVE: Core & Shield + IBIT capped 5%** | 9.28 | 7.82 | 1.18 | -14.11 | 41.64 | 52.70 | 3.70 | 16.46 | 0 |
| Core & Shield WITHOUT IBIT (previous live) | 6.48 | 6.88 | 0.95 | -14.61 | 43.71 | 44.36 | 3.82 | 15.36 | 0 |
| Core & Shield + IBIT uncapped (10% slots) | 12.71 | 9.99 | 1.25 | -15.32 | 41.84 | 64.32 | 3.84 | 13.86 | 0 |
| Shield alone (RAAM, live rules) | 9.16 | 8.32 | 1.10 | -14.71 | 18.65 | 41.11 | 7.12 | 32.93 | 0 |
| RAAM alone, original paper rules (v1, no IBIT) | 2.79 | 6.19 | 0.48 | -15.34 | 31.91 | 26.01 | 7.95 | 24.14 | 0 |
| Core & Shield 70/30 (42% SPY, 28% AGG, 30% RAAM) | 10.44 | 9.20 | 1.13 | -15.95 | 52.05 | 61.97 | 2.51 | 8.84 | 1 |
| Core & Shield 30/70 (18% SPY, 12% AGG, 70% RAAM) | 7.91 | 6.81 | 1.15 | -11.21 | 32.37 | 43.42 | 5.02 | 24.09 | 0 |
| Core & Shield with trend filter on | 8.91 | 8.08 | 1.10 | -15.37 | 45.96 | 53.72 | 4.29 | 15.21 | 0 |
| Core & Shield, SHY as cash | 9.10 | 7.82 | 1.16 | -14.53 | 42.22 | 52.42 | 3.72 | 16.21 | 0 |
| IBIT flattened to 0%/yr (hindsight check) | 7.58 | 7.53 | 1.01 | -14.61 | 43.22 | 47.88 | 3.78 | 16.43 | 0 |

### The same variants, out-of-sample only (2020 → now)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Down capture % | Up capture % |
|---|---|---|---|---|---|---|
| **LIVE: Core & Shield + IBIT capped 5%** | 9.17 | 8.51 | 1.08 | -11.06 | 45.50 | 51.63 |
| Core & Shield WITHOUT IBIT (previous live) | 8.11 | 7.88 | 1.03 | -11.06 | 45.70 | 48.49 |
| Core & Shield + IBIT uncapped (10% slots) | 11.13 | 10.07 | 1.10 | -11.43 | 46.70 | 58.26 |
| Shield alone (RAAM, live rules) | 8.64 | 7.81 | 1.10 | -6.72 | 21.68 | 37.88 |
| RAAM alone, original paper rules (v1, no IBIT) | 4.47 | 7.20 | 0.64 | -9.71 | 36.54 | 32.95 |
| Core & Shield 70/30 (42% SPY, 28% AGG, 30% RAAM) | 9.77 | 10.22 | 0.97 | -14.39 | 57.22 | 59.74 |
| Core & Shield 30/70 (18% SPY, 12% AGG, 70% RAAM) | 8.21 | 7.28 | 1.12 | -7.92 | 35.49 | 43.48 |
| Core & Shield with trend filter on | 8.35 | 8.86 | 0.95 | -12.31 | 51.24 | 52.23 |
| Core & Shield, SHY as cash | 8.75 | 8.56 | 1.03 | -12.98 | 47.07 | 51.19 |
| IBIT flattened to 0%/yr (hindsight check) | 8.13 | 8.28 | 0.99 | -11.06 | 46.03 | 48.81 |

## 3. 2008 stress test: Scenario B, IGOV spliced from BWX (entries Jun-2008 → Jun-2009). Bitcoin did not exist, so the rows run the rules WITHOUT IBIT
| Variant | CAGR % | Vol % | MaxDD % (monthly) | Worst month % | Total % | Months |
|---|---|---|---|---|---|---|
| Core & Shield (no IBIT) | -6.85 | 12.86 | -17.35 | -5.42 | -7.40 | 13 |
| Shield alone (RAAM) | 1.48 | 9.91 | -9.63 | -3.36 | 1.60 | 13 |
| 60/40 | -16.48 | 19.94 | -27.57 | -10.24 | -17.72 | 13 |
| SPY | -29.80 | 31.15 | -43.45 | -16.04 | -31.84 | 13 |
| Equal-weight 7Twelve | -22.44 | 28.54 | -37.43 | -16.35 | -24.07 | 13 |

Scenario B live-config breaker trips: [('2009-02-23', -20.2, -0.9)].

## 4. Calendar years (Scenario A)
| Year | Core & Shield % | Shield alone % | 60/40 % | SPY % | EW 7Twelve % | C&S avg cash % |
|---|---|---|---|---|---|---|
| 2015 | -0.2 | -1.5 | 1.1 | 2.3 | -5.7 | 22 |
| 2016 | 8.9 | 8.1 | 9.6 | 14.7 | 12.1 | 13 |
| 2017 | 28.9 | 45.1 | 14.1 | 21.3 | 13.3 | 12 |
| 2018 | -7.0 | -10.7 | -3.3 | -6.4 | -8.2 | 26 |
| 2019 | 19.6 | 15.2 | 23.7 | 34.0 | 18.6 | 8 |
| 2020 | 15.4 | 15.5 | 14.7 | 18.2 | 9.8 | 16 |
| 2021 | 16.1 | 16.5 | 15.6 | 28.6 | 14.7 | 11 |
| 2022 | -8.8 | -2.5 | -15.2 | -18.0 | -12.3 | 37 |
| 2023 | 8.8 | 1.7 | 16.2 | 24.7 | 9.6 | 19 |
| 2024 | 13.5 | 10.9 | 16.1 | 26.4 | 6.9 | 10 |
| 2025 | 10.5 | 7.5 | 13.5 | 17.7 | 12.5 | 8 |
| 2026 | 8.5 | 10.0 | 7.0 | 13.4 | 10.7 | 17 |

## 5. How often each ETF was held, live config (% of months; SPY and AGG are always held via the Core)
AGG 100% · SPY 100% · BIL 87.9% · TIP 59.3% · IBIT 52.1% · DBC 40.7% · IGOV 35.7% · RWR 33.6% · VV 33.6% · IJR 14.3% · EEM 12.9% · VAW 10% · EFA 10% · IJH 4.3%

![equity](equity_curve.png)
