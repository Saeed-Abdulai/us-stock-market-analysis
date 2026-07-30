"""
04_feature_engineering.py
Compute Daily_Return, MA20, MA50, Volatility_20d per ticker using DuckDB
window functions (memory-efficient - no giant pandas groupby needed).
"""
import duckdb

con = duckdb.connect()
con.execute("PRAGMA memory_limit='2GB'")

print("Computing features via DuckDB window functions...")

query = """
COPY (
    WITH raw_returns AS (
        SELECT
            *,
            (Close / LAG(Close) OVER (PARTITION BY Ticker ORDER BY Date)) - 1 AS Raw_Daily_Return
        FROM 'cleaned-data/all_prices_clean.parquet'
    ),
    windowed AS (
        SELECT
            * EXCLUDE (Raw_Daily_Return),
            -- Data-error guard: a handful of tickers have corrupted rows producing
            -- impossible one-day moves (e.g. 8000x jumps). Treat |return| > 100% as
            -- a data artifact and null it out rather than let it poison rolling stats.
            CASE WHEN ABS(Raw_Daily_Return) > 1.0 THEN NULL ELSE Raw_Daily_Return END AS Daily_Return,
            AVG(Close) OVER (
                PARTITION BY Ticker ORDER BY Date
                ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
            ) AS MA20,
            AVG(Close) OVER (
                PARTITION BY Ticker ORDER BY Date
                ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
            ) AS MA50
        FROM raw_returns
    )
    SELECT
        *,
        STDDEV(Daily_Return) OVER (
            PARTITION BY Ticker ORDER BY Date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) * SQRT(252) AS Volatility_20d
    FROM windowed
    ORDER BY Ticker, Date
) TO 'cleaned-data/all_prices_features.parquet' (FORMAT PARQUET)
"""
con.execute(query)

stats = con.execute("""
    SELECT COUNT(*), COUNT(DISTINCT Ticker) FROM 'cleaned-data/all_prices_features.parquet'
""").fetchall()
print("Feature rows, tickers:", stats)

sample = con.execute("""
    SELECT Ticker, Date, Close, Daily_Return, MA20, MA50, Volatility_20d
    FROM 'cleaned-data/all_prices_features.parquet'
    WHERE Ticker = 'AAPL'
    ORDER BY Date DESC
    LIMIT 5
""").fetchall()
print("Sample AAPL rows:", sample)

print("Saved cleaned-data/all_prices_features.parquet")
