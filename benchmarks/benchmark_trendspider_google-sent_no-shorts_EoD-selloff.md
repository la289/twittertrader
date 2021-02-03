## Benchmark Report

This breakdown of the analysis results and market performance validates the current implementation against historical data.

Use this command to regenerate the benchmark report after changes to the algorithm or data:
```shell
$ python benchmark.py > benchmark.md
```

### Events overview

Here's each tweet with the results of its analysis and individual market performance.

##### [1/5/2021 12:31 PM (Tuesday)](https://twitter.com/Trendspider_J/status/1346509715472224256)

> Launchpad.... engaged! $MRO #MRO https://t.co/SaisuxSwpH

*Strategy*

Company | Root | Sentiment | Strategy | Reason
--------|------|-----------|----------|-------
Marathon Oil | - | 0.5 :thumbsup: | bull | positive sentiment

*Performance*

Ticker | Exchange | Price @ tweet | Price @ close | Gain
-------|----------|---------------|---------------|-----
MRO | New York Stock Exchange | $7.58 | $7.47 | -1.516%

### Fund simulation

This is how an initial investment of $100,000.00 would have grown, including fees of 2 × $0.00 per pair of orders. Bold means that the data was used to trade.

Time | Trade | Gain | Value | Return | Annualized
-----|-------|------|-------|--------|-----------
*Initial* | - | - | *$100,000.00* | - | -
**1/5/2021 12:31 PM** | **MRO :thumbsup:** | -1.516% | $98,499.02 | -1.501% | -60.149%
