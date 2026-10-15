# Robustness: does the ranking have skill?

Generated 2026-10-15 by `backtest/robustness.py`. Same engine, data, costs (5 bps), dates, cash test, Bitcoin cap and breaker as the live backtest. **Context only:** nothing here changes the strategy or the evaluation criteria.

## Window A: 2015–2026, live rules (with Bitcoin) (from 2015-02-02, 140 months)

### Whole portfolio (Core & Shield)

| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |
|---|---|---|---|---|---|
| **Live ranking** (momentum + volatility + correlation) | 11.8% | 1.20 | −11.7% | −15.4% | 72% |
| Momentum only (top 5) | 12.8% | 1.11 | −14.9% | −18.9% | 91% |
| No ranking (all 12, equal slots) | 12.0% | 1.16 | −14.1% | −18.3% | 79% |
| Random 5 picks (1,000 runs): 5th / 50th / 95th percentile | 9.2 / 10.3 / 11.4 | 0.94 / 1.04 / 1.16 | −15.6 / −14.0 / −12.3 | −19.7 / −17.9 / −16.1 | 73.5 / 79.6 / 85.6 |

**Live ranking beats 99% of random portfolios on Sharpe**, 98% on return, 99% on worst daily drop and 98% on down-market defence.

### Shield on its own

| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |
|---|---|---|---|---|---|
| **Live ranking** (momentum + volatility + correlation) | 8.9% | 1.08 | −10.7% | −14.7% | 27% |
| Momentum only (top 5) | 11.1% | 0.94 | −12.0% | −15.9% | 66% |
| No ranking (all 12, equal slots) | 9.7% | 1.14 | −8.3% | −11.0% | 39% |
| Random 5 picks (1,000 runs): 5th / 50th / 95th percentile | 4.2 / 6.4 / 8.6 | 0.58 / 0.83 / 1.08 | −17.5 / −11.4 / −7.8 | −19.9 / −13.9 / −10.3 | 28.4 / 40.0 / 51.9 |

**Live ranking beats 95% of random portfolios on Sharpe**, 97% on return, 40% on worst daily drop and 97% on down-market defence.

## Window B: 2008–2026, live rules without Bitcoin (from 2008-03-03, 223 months)

### Whole portfolio (Core & Shield)

| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |
|---|---|---|---|---|---|
| **Live ranking** (momentum + volatility + correlation) | 8.8% | 0.99 | −12.3% | −16.1% | 69% |
| Momentum only (top 5) | 9.7% | 0.88 | −19.8% | −21.2% | 93% |
| No ranking (all 12, equal slots) | 8.8% | 0.93 | −14.1% | −18.2% | 77% |
| Random 5 picks (1,000 runs): 5th / 50th / 95th percentile | 8.0 / 8.6 / 9.2 | 0.84 / 0.90 / 0.97 | −15.8 / −14.2 / −12.7 | −19.8 / −18.2 / −16.6 | 73.9 / 77.4 / 81.2 |

**Live ranking beats 98% of random portfolios on Sharpe**, 66% on return, 98% on worst daily drop and 100% on down-market defence.

### Shield on its own

| Rule | Return / yr | Sharpe | Worst month-end drop | Worst daily drop | Share of 60/40's down-month losses |
|---|---|---|---|---|---|
| **Live ranking** (momentum + volatility + correlation) | 4.4% | 0.76 | −10.8% | −12.3% | 32% |
| Momentum only (top 5) | 6.3% | 0.61 | −20.6% | −22.1% | 85% |
| No ranking (all 12, equal slots) | 4.7% | 0.73 | −9.7% | −12.2% | 48% |
| Random 5 picks (1,000 runs): 5th / 50th / 95th percentile | 3.1 / 4.3 / 5.5 | 0.45 / 0.62 / 0.79 | −17.2 / −12.9 / −9.9 | −19.3 / −15.3 / −12.2 | 41.8 / 48.9 / 56.5 |

**Live ranking beats 92% of random portfolios on Sharpe**, 56% on return, 94% on worst daily drop and 100% on down-market defence.

### Test 2: long history without Bitcoin (2008-03-03 → 2026-09-25)

| Period | Strategy | Return / yr | Sharpe | Worst month-end drop | Months |
|---|---|---|---|---|---|
| Full period | C&S (no Bitcoin) | 8.8% | 0.99 | −12.3% | 223 |
| Full period | 60/40 | 8.5% | 0.85 | −30.2% | 223 |
| Full period | SPY | 12.0% | 0.78 | −47.2% | 223 |
| 2008–09 (crisis) | C&S (no Bitcoin) | 10.1% | 1.09 | −8.9% | 22 |
| 2008–09 (crisis) | 60/40 | −1.4% | −0.00 | −30.2% | 22 |
| 2008–09 (crisis) | SPY | −6.5% | −0.13 | −47.2% | 22 |
| 2010–14 | C&S (no Bitcoin) | 8.3% | 0.96 | −10.7% | 60 |
| 2010–14 | 60/40 | 11.0% | 1.42 | −8.7% | 60 |
| 2010–14 | SPY | 15.2% | 1.15 | −17.1% | 60 |
| 2015–19 | C&S (no Bitcoin) | 4.6% | 0.65 | −11.5% | 60 |
| 2015–19 | 60/40 | 8.4% | 1.08 | −8.4% | 60 |
| 2015–19 | SPY | 11.6% | 0.91 | −15.3% | 60 |
| 2020–26 | C&S (no Bitcoin) | 11.9% | 1.19 | −12.3% | 81 |
| 2020–26 | 60/40 | 9.5% | 0.85 | −19.2% | 81 |
| 2020–26 | SPY | 15.4% | 0.92 | −23.3% | 81 |

Worst daily drop −16.1% on 2020-05-01; breaker trips: [('2020-03-12', -16.0, -5.2)]. Beat 60/40 in 47% of rolling 12-month windows; ahead of 60/40 in 9 of 19 calendar years.

| Year | C&S (no Bitcoin) | 60/40 | SPY | Avg cash |
|---|---|---|---|---|
| 2008 | −7.4% | −17.2% | −30.4% | 71% |
| 2009 | 28.9% | 17.8% | 27.1% | 27% |
| 2010 | 2.8% | 11.9% | 15.0% | 16% |
| 2011 | 2.6% | 5.3% | 2.9% | 28% |
| 2012 | 7.7% | 11.1% | 16.1% | 15% |
| 2013 | 16.3% | 16.0% | 29.3% | 24% |
| 2014 | 12.5% | 11.0% | 14.4% | 8% |
| 2015 | −4.8% | -0.0% | −0.8% | 32% |
| 2016 | −0.7% | 9.6% | 14.7% | 23% |
| 2017 | 19.7% | 14.1% | 21.3% | 8% |
| 2018 | 2.6% | −3.3% | −6.4% | 33% |
| 2019 | 8.1% | 23.7% | 34.0% | 20% |
| 2020 | 14.7% | 14.7% | 18.2% | 18% |
| 2021 | 22.0% | 15.6% | 28.6% | 9% |
| 2022 | −3.6% | −15.2% | −18.0% | 82% |
| 2023 | 17.2% | 16.2% | 24.7% | 22% |
| 2024 | 15.7% | 16.1% | 26.4% | 8% |
| 2025 | 9.6% | 13.5% | 17.7% | 17% |
| 2026 | 6.7% | 7.0% | 13.4% | 22% |

