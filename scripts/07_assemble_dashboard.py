"""
07_assemble_dashboard.py
Assemble the final interactive dashboard HTML: KPI cards, all charts,
and a written insights/recommendations section, using a dark
finance-terminal theme.
"""
import json
import pandas as pd

with open("outputs/figures/divs.json") as f:
    divs = json.load(f)

ts = pd.read_parquet("cleaned-data/ticker_summary.parquet")
comparison = pd.read_excel("outputs/Stock_Market_Summary_Tables.xlsx", sheet_name="Stocks_vs_ETFs")

TOTAL_TICKERS = 7930
TOTAL_ROWS = 17430367
STOCKS_N = int(comparison.loc[comparison.AssetType == "Stock", "Num_Tickers"].iloc[0])
ETFS_N = int(comparison.loc[comparison.AssetType == "ETF", "Num_Tickers"].iloc[0])
MEDIAN_RET = ts["Annualized_Return"].median()
MEDIAN_VOL = ts["Annualized_Volatility"].median()
STOCK_VOL = float(comparison.loc[comparison.AssetType == "Stock", "Avg_Annualized_Volatility"].iloc[0])
ETF_VOL = float(comparison.loc[comparison.AssetType == "ETF", "Avg_Annualized_Volatility"].iloc[0])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>US Stock Market Analysis — 1962-2017</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0B0E14;
    --panel: #12161F;
    --panel-border: #232837;
    --text: #E5E9F0;
    --muted: #7C8699;
    --green: #00D68F;
    --red: #FF4757;
    --blue: #3B82F6;
    --amber: #F5A623;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
  }}
  .mono {{ font-family: 'JetBrains Mono', monospace; }}
  header {{
    padding: 36px 40px 24px;
    border-bottom: 1px solid var(--panel-border);
  }}
  header h1 {{
    margin: 0 0 6px;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
  }}
  header h1 span {{ color: var(--green); }}
  header p {{
    margin: 0;
    color: var(--muted);
    font-size: 14px;
  }}
  .kpi-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px;
    padding: 28px 40px;
  }}
  .kpi {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 18px 20px;
  }}
  .kpi .label {{
    color: var(--muted);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }}
  .kpi .value {{
    font-size: 26px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
  }}
  .kpi .value.green {{ color: var(--green); }}
  .kpi .value.blue {{ color: var(--blue); }}
  .kpi .value.amber {{ color: var(--amber); }}
  main {{
    padding: 0 40px 40px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }}
  .full {{ grid-column: 1 / -1; }}
  .chart-card {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 8px 12px 4px;
  }}
  section.insights {{
    padding: 10px 40px 60px;
  }}
  section.insights h2 {{
    font-size: 20px;
    border-left: 4px solid var(--green);
    padding-left: 12px;
    margin-bottom: 18px;
  }}
  .insight-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 18px;
  }}
  .insight-card {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-left: 3px solid var(--blue);
    border-radius: 8px;
    padding: 18px 20px;
  }}
  .insight-card.gain {{ border-left-color: var(--green); }}
  .insight-card.risk {{ border-left-color: var(--red); }}
  .insight-card.note {{ border-left-color: var(--amber); }}
  .insight-card h3 {{
    margin: 0 0 8px;
    font-size: 15px;
    color: var(--text);
  }}
  .insight-card p {{
    margin: 0;
    color: var(--muted);
    font-size: 13.5px;
    line-height: 1.55;
  }}
  footer {{
    padding: 24px 40px 40px;
    color: var(--muted);
    font-size: 12px;
    border-top: 1px solid var(--panel-border);
  }}
  footer a {{ color: var(--blue); }}
  @media (max-width: 900px) {{
    main {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <h1>US Stock Market <span>Analysis</span></h1>
  <p>Daily OHLCV price history across the full US equity + ETF universe &middot; 1962&ndash;2017 &middot; Source: Kaggle "Huge Stock Market Dataset" (Boris Marjanovic)</p>
</header>

<div class="kpi-row">
  <div class="kpi">
    <div class="label">Total Tickers</div>
    <div class="value mono">{TOTAL_TICKERS:,}</div>
  </div>
  <div class="kpi">
    <div class="label">Total Price Records</div>
    <div class="value mono blue">{TOTAL_ROWS:,}</div>
  </div>
  <div class="kpi">
    <div class="label">Stocks / ETFs</div>
    <div class="value mono">{STOCKS_N:,} <span style="color:var(--muted); font-size:16px;">/</span> {ETFS_N:,}</div>
  </div>
  <div class="kpi">
    <div class="label">Median Ann. Return (2015-17)</div>
    <div class="value mono green">{MEDIAN_RET:.1%}</div>
  </div>
  <div class="kpi">
    <div class="label">Median Ann. Volatility</div>
    <div class="value mono amber">{MEDIAN_VOL:.1%}</div>
  </div>
</div>

<main>
  <div class="chart-card full">{divs['tech_performance']}</div>
  <div class="chart-card">{divs['risk_return']}</div>
  <div class="chart-card">{divs['top_gainers']}</div>
  <div class="chart-card">{divs['volume_trend']}</div>
  <div class="chart-card">{divs['volatility_trend']}</div>
  <div class="chart-card">{divs['most_liquid']}</div>
  <div class="chart-card">{divs['breadth_trend']}</div>
</main>

<section class="insights">
  <h2>Key Findings &amp; Takeaways</h2>
  <div class="insight-grid">
    <div class="insight-card gain">
      <h3>Big tech dominated 2010&ndash;2017</h3>
      <p>NVDA delivered roughly 10x total return between 2015 and 2017 alone, driven by the early GPU/gaming and data-center growth cycle &mdash; well before its later AI-era surge. AAPL, MSFT and AMZN all compounded steadily over the full window, reinforcing how concentrated market-cap-weighted gains were in a handful of names.</p>
    </div>
    <div class="insight-card risk">
      <h3>Stocks carry roughly double ETFs' volatility</h3>
      <p>Individual stocks averaged {STOCK_VOL:.0%} annualized volatility versus {ETF_VOL:.0%} for ETFs in 2015&ndash;2017. This is the diversification effect in action: an ETF bundles dozens to hundreds of names, so idiosyncratic single-stock shocks average out, while a single ticker is fully exposed to company-specific risk (earnings misses, guidance changes, litigation).</p>
    </div>
    <div class="insight-card">
      <h3>Risk and return are only loosely linked</h3>
      <p>The risk/return scatter shows a wide, noisy cloud rather than a clean upward slope &mdash; plenty of high-volatility tickers delivered flat or negative returns over the window, and several low-volatility names still posted solid gains. Volatility alone is a poor predictor of forward return over a 2&ndash;3 year horizon; it mainly signals how bumpy the ride will be, not the destination.</p>
    </div>
    <div class="insight-card note">
      <h3>Data quality mattered before any analysis</h3>
      <p>The raw dataset contained a small number of corrupted rows &mdash; a few tickers showed one-day price jumps of 1,000x or more, almost certainly data-entry or feed errors rather than real market moves. These were detected by inspecting extreme daily returns and excluded from all rolling volatility and return calculations; leaving them in inflated average stock volatility roughly 175x above realistic levels.</p>
    </div>
    <div class="insight-card">
      <h3>Trading volume grew steadily through the decade</h3>
      <p>Aggregate monthly trading volume across both stocks and ETFs shows a general upward drift from 2010 to 2017, consistent with rising market participation, the growth of ETF products as a category, and the increasing role of algorithmic/high-frequency trading over the period.</p>
    </div>
    <div class="insight-card">
      <h3>Liquidity concentrates in a small set of names</h3>
      <p>The most-traded tickers by average daily volume are dominated by large index ETFs and a handful of mega-cap stocks &mdash; these names carry the tightest bid/ask spreads and lowest transaction-cost friction, which matters directly for anyone building or backtesting a systematic trading strategy on this data.</p>
    </div>
  </div>
</section>

<footer>
  Dataset: <a href="https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs" target="_blank">Huge Stock Market Dataset</a> (Kaggle, Boris Marjanovic) &middot;
  Daily OHLCV for {TOTAL_TICKERS:,} NYSE/NASDAQ/NYSE MKT tickers, last updated Nov 2017 &middot;
  Analysis: pandas, DuckDB, Plotly &middot; Built by Saeed Abdulai
</footer>

</body>
</html>
"""

with open("outputs/Stock_Market_Dashboard.html", "w") as f:
    f.write(html)

print("Dashboard written:", len(html), "chars")
