"""
03_clean_data.py
Clean the raw combined stock/ETF price dataset using DuckDB (memory-efficient
streaming SQL engine) rather than loading all 17.4M rows into pandas at once.
"""
import duckdb

con = duckdb.connect()
con.execute("PRAGMA memory_limit='2GB'")

print("Cleaning data via DuckDB streaming query...")

query = """
COPY (
    WITH base AS (
        SELECT
            CAST(Date AS DATE) AS Date,
            Open, High, Low, Close, Volume,
            Ticker, AssetType
        FROM 'all_prices_raw.parquet'
        WHERE Open > 0 AND High > 0 AND Low > 0 AND Close > 0
          AND High >= Low
    ),
    counts AS (
        SELECT Ticker, COUNT(*) AS n
        FROM base
        GROUP BY Ticker
        HAVING COUNT(*) >= 100
    )
    SELECT b.*
    FROM base b
    JOIN counts c ON b.Ticker = c.Ticker
    ORDER BY b.Ticker, b.Date
) TO 'cleaned-data/all_prices_clean.parquet' (FORMAT PARQUET)
"""
con.execute(query)

# Report stats
stats = con.execute("""
    SELECT COUNT(*), COUNT(DISTINCT Ticker), MIN(Date), MAX(Date)
    FROM 'cleaned-data/all_prices_clean.parquet'
""").fetchall()
print("Clean rows, unique tickers, min date, max date:", stats)

asset_split = con.execute("""
    SELECT AssetType, COUNT(*), COUNT(DISTINCT Ticker)
    FROM 'cleaned-data/all_prices_clean.parquet'
    GROUP BY AssetType
""").fetchall()
print("By asset type:", asset_split)

print("Saved cleaned-data/all_prices_clean.parquet")
