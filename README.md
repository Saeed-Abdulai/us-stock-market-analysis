# US Stock Market Analysis (1962–2017)

An end-to-end analysis of daily price/volume history across the **full US
equity and ETF universe** — 7,930 tickers, 17.4 million price records —
exploring performance, volatility, liquidity, and risk/return patterns
across more than five decades of market data.

**[View the interactive dashboard](Stock_Market_Dashboard.html)**

## Dataset

[Huge Stock Market Dataset](https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs)
(Kaggle, Boris Marjanovic) — daily OHLCV history for all NYSE, NASDAQ, and
NYSE MKT stocks and ETFs, prices adjusted for dividends/splits. Last updated
November 2017. One `.us.txt` file per ticker, ~8,500 files total.

## Key Findings

- **Big tech dominated 2010–2017.** NVDA delivered roughly 10x total return
  between 2015–2017 alone — well before the later AI-driven surge —
  reflecting the earlier GPU/gaming and data-center growth cycle.
- **Stocks carry roughly double ETFs' volatility** (≈50% vs ≈26%
  annualized in 2015–2017), a direct illustration of the diversification
  effect: an ETF bundles many names, smoothing out company-specific shocks.
- **Risk and return are only loosely linked** over a 2–3 year horizon.
  The risk/return scatter shows a wide, noisy cloud rather than a clean
  trend line — high volatility doesn't reliably predict higher return.
- **Trading volume grew steadily from 2010 to 2017**, consistent with
  rising market participation, ETF adoption, and algorithmic trading.
- **Liquidity concentrates in a small set of names** — the most-traded
  tickers are dominated by large index ETFs and mega-cap stocks, which
  matters directly for anyone backtesting a systematic trading strategy
  on this kind of data.

## Data Quality Note

The raw dataset contained a small number of corrupted rows — a handful of
tickers (e.g. `MTBCP`) showed impossible one-day price jumps of 1,000x or
more, almost certainly feed/data-entry errors rather than real market
moves. Left uncorrected, these single bad rows inflated *average stock
volatility from a realistic ~50% up to a nonsensical ~8,877%* — a good
reminder that a single data quality check can make or break every
downstream statistic. These rows were detected by ranking absolute daily
returns and excluding any |return| > 100% from rolling volatility/return
calculations before any aggregation (see `04_feature_engineering.py`).

## Methodology / Pipeline

| Step | Script | What it does |
|---|---|---|
| 1 | `01_load_data.py`* | Load all per-ticker `.us.txt` files, tag Stock/ETF, stream-write to a single Parquet file |
| 2 | `02_eda.py`* | Initial profiling (shape, missing values, date range) |
| 3 | `03_clean_data.py` | Remove invalid prices, drop tickers with <100 trading days |
| 4 | `04_feature_engineering.py` | Daily return, MA20, MA50, 20-day annualized volatility — with the outlier guard above |
| 5 | `05_build_tables.py` | Per-ticker summary stats, top/bottom gainers, most/least volatile, Stocks vs ETFs comparison, yearly/monthly aggregates |
| 5b | `05b_format_excel.py` | Professional formatting (fonts, number formats, headers) on the Excel workbook |
| 6 | `06_make_figures.py` | 7 interactive Plotly charts |
| 7 | `07_assemble_dashboard.py` | Assembles the final HTML dashboard with KPI cards and written insights |

\* Scripts 01 and 02 are the ones originally used to build the raw combined
Parquet file from the individual ticker CSVs — see the note below on
memory-efficient reproduction if working with the full dataset locally.

## A Note on Memory (Important if Reproducing Locally)

The full dataset is 17.4M rows — attempting to load, clean, and aggregate
that in plain `pandas` (especially under pandas 3.x's default string
dtype handling) needs several GB of free RAM and can trigger
`ArrayMemoryError` on machines with limited memory, even for operations
as simple as `df.isna().sum()`.

Scripts `03` through `05` in this package instead use **DuckDB**, a
lightweight SQL engine that streams and processes Parquet files without
loading the full dataset into memory at once. It comfortably handled the
entire 17.4M-row dataset within a 2GB memory limit. If your machine
struggles with the pandas-based approach, installing DuckDB
(`pip install duckdb`) and using SQL for the heavy aggregation steps is
worth trying — it may solve the memory problem without needing more RAM
at all.

## Tech Stack

`Python` · `pandas` · `DuckDB` · `Plotly` · `openpyxl` · `PyArrow`

## Files

```
US-Stock-Market-Analysis/
├── Stock_Market_Dashboard.html      # Interactive dashboard (open in any browser)
├── Stock_Market_Summary_Tables.xlsx # 7-sheet Excel workbook of summary stats
├── scripts/                          # Full analysis pipeline (03-07)
├── cleaned-data/                     # Small aggregated tables (safe for GitHub)
└── README.md
```

Note: the large intermediate Parquet files (`all_prices_clean.parquet`,
`all_prices_features.parquet`, ~400MB–900MB) are **not included** here —
only the small, already-aggregated summary tables needed to reproduce the
charts are kept, to stay well under GitHub's file size limits.

## Author

Saeed Abdulai
