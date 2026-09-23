# RAAM Backtest Report

Generated 2026-09-23 by `backtest/backtest.py`. Costs: 5 bps per side on turnover.
Engine: the live `scripts/raam.py compute_signal()` with `config/raam.json`. Signal at the month-end close; fill at the next open.
Data: Yahoo Finance adjusted daily OHLC. Past results do not guarantee future results.

## 1. Headline: Scenario A, real data only (2009-07-01 → 2026-09-23)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Worst month % | % months up | Months |
|---|---|---|---|---|---|---|---|
| RAAM baseline — full | 4.03 | 6.30 | 0.66 | -11.78 | -5.42 | 61.84 | 207 |
| RAAM baseline — 2009-2019 (in-sample) | 3.78 | 5.67 | 0.68 | -10.17 | -4.68 | 62.70 | 126 |
| RAAM baseline — 2020-now (out-of-sample) | 4.44 | 7.22 | 0.64 | -9.71 | -5.42 | 60.49 | 81 |
| SPY — full | 15.08 | 14.79 | 1.03 | -23.31 | -16.35 | 71.01 | 207 |
| SPY — 2009-2019 (in-sample) | 14.96 | 13.05 | 1.14 | -17.10 | -11.73 | 73.02 | 126 |
| SPY — 2020-now (out-of-sample) | 15.27 | 17.22 | 0.92 | -23.31 | -16.35 | 67.90 | 81 |
| Equal-weight 7Twelve — full | 7.64 | 10.76 | 0.74 | -20.18 | -14.34 | 64.25 | 207 |
| Equal-weight 7Twelve — 2009-2019 (in-sample) | 7.85 | 9.74 | 0.83 | -15.27 | -9.27 | 65.87 | 126 |
| Equal-weight 7Twelve — 2020-now (out-of-sample) | 7.31 | 12.25 | 0.64 | -18.25 | -14.34 | 61.73 | 81 |

The Sharpe uses rf = 0.

**Daily-path risk (baseline):**
- Max drawdown **-16.2%**, reached on 2020-03-18. SPY's max drawdown over the same span was -33.7%.
- Worst single day **-3.1%**.
- Circuit breaker (−15% from peak or −5% in one day) would have tripped **2** time(s): [('2020-03-18', -16.2, -1.5), ('2025-04-07', -15.4, -1.5)].

## 2. Pre-registered variants (Scenario A, full period)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Worst month % | Turnover/yr | Avg SHY % |
|---|---|---|---|---|---|---|---|
| Baseline (current config) | 4.03 | 6.30 | 0.66 | -11.78 | -5.42 | 7.67 | 22.71 |
| A3 lower band literal (+ATR) | 4.55 | 5.91 | 0.78 | -10.24 | -4.68 | 7.14 | 24.25 |
| A4 vol = Parkinson (H/L) | 3.93 | 6.26 | 0.65 | -15.70 | -5.40 | 7.77 | 22.80 |
| A4 vol = Garman-Klass (OHLC) | 4.10 | 6.26 | 0.67 | -15.25 | -5.40 | 7.87 | 22.22 |
| A5 tiebreak literal (+M/x) | 3.98 | 6.09 | 0.67 | -11.07 | -5.42 | 7.64 | 24.44 |
| A1 momentum-heavy 50/25/25 | 5.67 | 7.99 | 0.73 | -13.18 | -7.58 | 8.45 | 16.14 |
| Check: momentum only 100/0/0 | 7.44 | 10.64 | 0.73 | -15.93 | -9.25 | 7.51 | 10.82 |
| Check: no ATR trend filter | 4.68 | 5.87 | 0.81 | -10.24 | -4.68 | 7.00 | 24.25 |

### The same variants, out-of-sample only (2020 → now)
| Variant | CAGR % | Vol % | Sharpe | MaxDD % (monthly) | Worst month % |
|---|---|---|---|---|---|
| Baseline (current config) | 4.44 | 7.22 | 0.64 | -9.71 | -5.42 |
| A3 lower band literal (+ATR) | 5.82 | 6.34 | 0.93 | -10.07 | -4.65 |
| A4 vol = Parkinson (H/L) | 5.38 | 7.26 | 0.76 | -7.08 | -5.40 |
| A4 vol = Garman-Klass (OHLC) | 5.28 | 7.27 | 0.75 | -7.51 | -5.40 |
| A5 tiebreak literal (+M/x) | 3.86 | 7.23 | 0.56 | -9.55 | -5.42 |
| A1 momentum-heavy 50/25/25 | 5.67 | 8.42 | 0.70 | -13.18 | -5.38 |
| Check: momentum only 100/0/0 | 7.66 | 11.24 | 0.71 | -14.55 | -6.76 |
| Check: no ATR trend filter | 6.02 | 6.32 | 0.96 | -9.65 | -4.65 |

## 3. 2008 stress test: Scenario B, with IGOV spliced from BWX (entries Jun-2008 → Jun-2009)
Scenario B's first rebalance is 2008-03-03.
| Variant | CAGR % | Vol % | MaxDD % (monthly) | Worst month % | Total % | Months |
|---|---|---|---|---|---|---|
| RAAM (BWX-spliced) | 3.54 | 9.59 | -7.33 | -3.25 | 3.84 | 13 |
| SPY | -29.80 | 31.15 | -43.45 | -16.04 | -31.84 | 13 |
| Equal-weight 7Twelve | -22.44 | 28.54 | -37.43 | -16.35 | -24.07 | 13 |

Scenario B daily max drawdown over its full history: **-16.2%** (2020-03-18). Breaker trips: [('2020-03-18', -16.2, -1.5), ('2025-04-07', -15.4, -1.5)].

## 4. Calendar years (Scenario A baseline)
| Year | RAAM % | SPY % | EW 7Twelve % | Avg SHY weight % |
|---|---|---|---|---|
| 2009 | 10.5 | 22.9 | 18.9 | 0 |
| 2010 | 11.4 | 15.0 | 14.3 | 13 |
| 2011 | 4.9 | 2.9 | 0.4 | 30 |
| 2012 | 4.5 | 16.1 | 11.9 | 13 |
| 2013 | 2.2 | 29.3 | 8.3 | 40 |
| 2014 | 3.2 | 14.4 | 2.8 | 10 |
| 2015 | -4.9 | -0.8 | -5.9 | 45 |
| 2016 | -2.2 | 14.7 | 12.1 | 23 |
| 2017 | 11.1 | 21.3 | 13.3 | 10 |
| 2018 | -2.0 | -6.4 | -8.2 | 37 |
| 2019 | 2.6 | 34.0 | 18.6 | 12 |
| 2020 | 6.9 | 18.2 | 9.8 | 20 |
| 2021 | 14.6 | 28.6 | 14.7 | 18 |
| 2022 | -6.6 | -18.0 | -12.3 | 67 |
| 2023 | -0.6 | 24.7 | 9.6 | 28 |
| 2024 | -1.0 | 26.4 | 6.9 | 5 |
| 2025 | 7.5 | 17.7 | 12.5 | 12 |
| 2026 | 10.8 | 12.8 | 10.7 | 11 |

## 5. How often each ETF was held (% of months)
AGG 67.6% · TIP 67.6% · SHY 51.2% · IGOV 45.4% · RWR 41.1% · DBC 40.1% · VV 33.3% · IJR 25.6% · EFA 17.9% · VAW 17.4% · EEM 15.9% · IJH 14.5%

![equity](equity_curve.png)
