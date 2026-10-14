# Robustness: does the ranking have skill?

Generated 2026-10-14 by `backtest/robustness.py`. Same engine, data, costs (5 bps), dates, cash test, IBIT cap and breaker as the live backtest. **Context only:** nothing here changes the strategy or the evaluation criteria.

## Window A: 2015–2026, live rules (with Bitcoin) (from 2015-02-02, 140 months)

### Whole portfolio (Core & Shield)

| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |
|---|---|---|---|---|---|
| **Live ranking** (momentum + volatility + correlation) | 9.3% | 1.18 | −11.1% | −14.1% | 63% |
| Momentum only (top 5) | 10.2% | 1.05 | −12.5% | −17.7% | 83% |
| No ranking (all 12, equal slots) | 9.6% | 1.18 | −11.2% | −14.5% | 69% |
| Random 5 picks (1,000 runs): 5th / 50th / 95th percentile | 6.8 / 7.9 / 9.0 | 0.89 / 1.02 / 1.17 | −13.5 / −11.3 / −9.6 | −16.3 / −14.5 / −13.1 | 64.2 / 70.1 / 75.9 |

**Live ranking beats 97% of random portfolios on Sharpe**, 98% on return, 66% on worst daily drop and 97% on down-market defence.

### Shield on its own

| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |
|---|---|---|---|---|---|
| **Live ranking** (momentum + volatility + correlation) | 9.2% | 1.10 | −10.7% | −14.7% | 26% |
| Momentum only (top 5) | 11.0% | 0.93 | −12.1% | −16.0% | 66% |
| No ranking (all 12, equal slots) | 9.8% | 1.14 | −8.5% | −11.0% | 39% |
| Random 5 picks (1,000 runs): 5th / 50th / 95th percentile | 4.3 / 6.4 / 8.6 | 0.58 / 0.82 / 1.08 | −17.8 / −11.6 / −7.9 | −20.2 / −14.0 / −10.3 | 28.4 / 40.2 / 52.1 |

**Live ranking beats 96% of random portfolios on Sharpe**, 98% on return, 41% on worst daily drop and 97% on down-market defence.

## Window B: 2008–2026, live rules without Bitcoin (from 2008-03-03, 223 months)

### Whole portfolio (Core & Shield)

| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |
|---|---|---|---|---|---|
| **Live ranking** (momentum + volatility + correlation) | 6.6% | 0.93 | −19.0% | −22.0% | 66% |
| Momentum only (top 5) | 7.5% | 0.79 | −25.2% | −27.9% | 93% |
| No ranking (all 12, equal slots) | 6.4% | 0.84 | −23.0% | −25.5% | 76% |
| Random 5 picks (1,000 runs): 5th / 50th / 95th percentile | 5.6 / 6.2 / 6.9 | 0.73 / 0.81 / 0.90 | −25.2 / −22.9 / −17.6 | −27.5 / −25.4 / −20.0 | 71.4 / 75.6 / 80.3 |

**Live ranking beats 98% of random portfolios on Sharpe**, 86% on return, 55% on worst daily drop and 100% on down-market defence.

### Shield on its own

| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |
|---|---|---|---|---|---|
| **Live ranking** (momentum + volatility + correlation) | 4.5% | 0.77 | −10.4% | −12.0% | 32% |
| Momentum only (top 5) | 6.4% | 0.62 | −19.7% | −22.1% | 84% |
| No ranking (all 12, equal slots) | 4.7% | 0.73 | −9.7% | −12.2% | 48% |
| Random 5 picks (1,000 runs): 5th / 50th / 95th percentile | 3.1 / 4.3 / 5.5 | 0.45 / 0.62 / 0.78 | −17.4 / −13.0 / −10.0 | −19.5 / −15.4 / −12.2 | 41.9 / 48.9 / 56.5 |

**Live ranking beats 94% of random portfolios on Sharpe**, 63% on return, 96% on worst daily drop and 100% on down-market defence.

### Test 2: long history without Bitcoin (2008-03-03 → 2026-09-25)

| Period | Strategy | Return / yr | Sharpe | Worst month-end drop | Months |
|---|---|---|---|---|---|
| Full period | C&S (no Bitcoin) | 6.6% | 0.93 | −19.0% | 223 |
| Full period | 60/40 | 8.5% | 0.85 | −30.2% | 223 |
| Full period | SPY | 12.0% | 0.78 | −47.2% | 223 |
| 2008–09 (crisis) | C&S (no Bitcoin) | 3.9% | 0.40 | −19.0% | 22 |
| 2008–09 (crisis) | 60/40 | −1.4% | −0.00 | −30.2% | 22 |
| 2008–09 (crisis) | SPY | −6.5% | −0.13 | −47.2% | 22 |
| 2010–14 | C&S (no Bitcoin) | 8.1% | 1.26 | −6.5% | 60 |
| 2010–14 | 60/40 | 11.0% | 1.42 | −8.7% | 60 |
| 2010–14 | SPY | 15.2% | 1.15 | −17.1% | 60 |
| 2015–19 | C&S (no Bitcoin) | 4.2% | 0.82 | −7.1% | 60 |
| 2015–19 | 60/40 | 8.4% | 1.08 | −8.4% | 60 |
| 2015–19 | SPY | 11.6% | 0.91 | −15.3% | 60 |
| 2020–26 | C&S (no Bitcoin) | 8.1% | 1.03 | −11.1% | 81 |
| 2020–26 | 60/40 | 9.5% | 0.85 | −19.2% | 81 |
| 2020–26 | SPY | 15.4% | 0.92 | −23.3% | 81 |

Worst daily drop −22.0% on 2009-03-09; breaker trips: [('2009-02-23', -20.2, -0.9)]. Beat 60/40 in 23% of rolling 12-month windows; ahead of 60/40 in 5 of 19 calendar years.

| Year | C&S (no Bitcoin) | 60/40 | SPY | Avg cash |
|---|---|---|---|---|
| 2008 | −11.4% | −17.2% | −30.4% | 26% |
| 2009 | 21.1% | 17.8% | 27.1% | 10% |
| 2010 | 10.8% | 11.9% | 15.0% | 7% |
| 2011 | 5.1% | 5.3% | 2.9% | 15% |
| 2012 | 7.7% | 11.1% | 16.1% | 7% |
| 2013 | 8.9% | 16.0% | 29.3% | 20% |
| 2014 | 8.0% | 11.0% | 14.4% | 8% |
| 2015 | −2.5% | -0.0% | −0.8% | 23% |
| 2016 | 3.7% | 9.6% | 14.7% | 11% |
| 2017 | 11.8% | 14.1% | 21.3% | 8% |
| 2018 | −3.8% | −3.3% | −6.4% | 25% |
| 2019 | 12.9% | 23.7% | 34.0% | 8% |
| 2020 | 11.5% | 14.7% | 18.2% | 14% |
| 2021 | 16.1% | 15.6% | 28.6% | 9% |
| 2022 | −7.8% | −15.2% | −18.0% | 37% |
| 2023 | 6.7% | 16.2% | 24.7% | 18% |
| 2024 | 10.3% | 16.1% | 26.4% | 8% |
| 2025 | 11.1% | 13.5% | 17.7% | 8% |
| 2026 | 8.5% | 7.0% | 13.4% | 17% |

