"""
05_build_tables.py
Build summary tables via DuckDB aggregation (heavy lifting stays out of
pandas), then export smaller aggregated results to Excel.
"""
import duckdb
import pandas as pd

con = duckdb.connect()
con.execute("PRAGMA memory_limit='2GB'")

FEAT = "'cleaned-data/all_prices_features.parquet'"

print("Building per-ticker summary stats (2015-2017 window for relevance)...")

ticker_summary = con.execute(f"""
    SELECT
        Ticker,
        AssetType,
        COUNT(*) AS Trading_Days,
        AVG(Daily_Return) * 252 AS Annualized_Return,
        STDDEV(Daily_Return) * SQRT(252) AS Annualized_Volatility,
        MIN(Date) AS First_Date,
        MAX(Date) AS Last_Date,
        FIRST(Close ORDER BY Date) AS First_Close,
        LAST(Close ORDER BY Date) AS Last_Close,
        (LAST(Close ORDER BY Date) / NULLIF(FIRST(Close ORDER BY Date),0) - 1) AS Total_Return
    FROM {FEAT}
    WHERE Date >= '2015-01-01'
    GROUP BY Ticker, AssetType
    HAVING COUNT(*) >= 250
""").df()
print("Ticker summary shape:", ticker_summary.shape)

top_gainers = ticker_summary.sort_values("Total_Return", ascending=False).head(20)
bottom_gainers = ticker_summary.sort_values("Total_Return", ascending=True).head(20)
most_volatile = ticker_summary.sort_values("Annualized_Volatility", ascending=False).head(20)
least_volatile = ticker_summary[ticker_summary["Annualized_Volatility"] > 0].sort_values("Annualized_Volatility", ascending=True).head(20)

print("Building Stocks vs ETFs comparison...")
asset_comparison = con.execute(f"""
    SELECT
        AssetType,
        COUNT(DISTINCT Ticker) AS Num_Tickers,
        AVG(Daily_Return) * 252 AS Avg_Annualized_Return,
        STDDEV(Daily_Return) * SQRT(252) AS Avg_Annualized_Volatility,
        AVG(Volume) AS Avg_Daily_Volume
    FROM {FEAT}
    WHERE Date >= '2015-01-01'
    GROUP BY AssetType
""").df()
print(asset_comparison)

print("Building yearly market summary...")
yearly_summary = con.execute(f"""
    SELECT
        EXTRACT(YEAR FROM Date) AS Year,
        AssetType,
        COUNT(DISTINCT Ticker) AS Active_Tickers,
        AVG(Daily_Return) * 252 AS Avg_Annualized_Return,
        STDDEV(Daily_Return) * SQRT(252) AS Avg_Annualized_Volatility,
        SUM(Volume) AS Total_Volume
    FROM {FEAT}
    GROUP BY Year, AssetType
    ORDER BY Year, AssetType
""").df()
print("Yearly summary shape:", yearly_summary.shape)

print("Building monthly aggregation (for Power-BI-style time series)...")
monthly_summary = con.execute(f"""
    SELECT
        DATE_TRUNC('month', Date) AS Month,
        AssetType,
        AVG(Close) AS Avg_Close,
        AVG(Daily_Return) AS Avg_Daily_Return,
        AVG(Volatility_20d) AS Avg_Volatility,
        SUM(Volume) AS Total_Volume,
        COUNT(DISTINCT Ticker) AS Active_Tickers
    FROM {FEAT}
    WHERE Date >= '2010-01-01'
    GROUP BY Month, AssetType
    ORDER BY Month, AssetType
""").df()
print("Monthly summary shape:", monthly_summary.shape)

print("Building sector-scale proxy: top 20 by average daily volume (liquidity leaders)...")
most_liquid = con.execute(f"""
    SELECT
        Ticker, AssetType,
        AVG(Volume) AS Avg_Daily_Volume,
        AVG(Close) AS Avg_Close
    FROM {FEAT}
    WHERE Date >= '2015-01-01'
    GROUP BY Ticker, AssetType
    ORDER BY Avg_Daily_Volume DESC
    LIMIT 20
""").df()

# Export to Excel — multi-sheet workbook
with pd.ExcelWriter("outputs/Stock_Market_Summary_Tables.xlsx", engine="openpyxl") as writer:
    top_gainers.to_excel(writer, sheet_name="Top_20_Gainers", index=False)
    bottom_gainers.to_excel(writer, sheet_name="Bottom_20_Gainers", index=False)
    most_volatile.to_excel(writer, sheet_name="Most_Volatile", index=False)
    least_volatile.to_excel(writer, sheet_name="Least_Volatile", index=False)
    asset_comparison.to_excel(writer, sheet_name="Stocks_vs_ETFs", index=False)
    yearly_summary.to_excel(writer, sheet_name="Yearly_Summary", index=False)
    most_liquid.to_excel(writer, sheet_name="Most_Liquid", index=False)

# Save monthly summary separately for chart-building (larger table)
monthly_summary.to_parquet("cleaned-data/monthly_summary.parquet", index=False)
ticker_summary.to_parquet("cleaned-data/ticker_summary.parquet", index=False)

print("Saved outputs/Stock_Market_Summary_Tables.xlsx")
print("Saved cleaned-data/monthly_summary.parquet and ticker_summary.parquet")
