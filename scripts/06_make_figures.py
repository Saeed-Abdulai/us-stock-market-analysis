"""
06_make_figures.py
Build all Plotly figures for the dashboard using a dark, finance-terminal
themed palette. Figures are saved as HTML div strings for later assembly.
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json

# ---- Theme ----
BG = "#0B0E14"
PANEL = "#12161F"
GRID = "#232837"
TEXT = "#E5E9F0"
MUTED = "#7C8699"
GREEN = "#00D68F"   # gains
RED = "#FF4757"     # losses
BLUE = "#3B82F6"    # stocks
AMBER = "#F5A623"   # ETFs / highlight
FONT = "JetBrains Mono, Consolas, monospace"

def base_layout(title, height=460):
    return dict(
        title=dict(text=title, font=dict(size=17, color=TEXT, family=FONT), x=0.02, xanchor="left"),
        paper_bgcolor=BG,
        plot_bgcolor=PANEL,
        font=dict(family=FONT, color=TEXT, size=12),
        margin=dict(l=60, r=30, t=60, b=50),
        height=height,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
    )

figs = {}

# ---- 1. Indexed price performance: AAPL, MSFT, NVDA, GOOGL, AMZN (2010=100) ----
samples = pd.read_parquet('cleaned-data/sample_tickers.parquet')
samples['Date'] = pd.to_datetime(samples['Date'])
fig1 = go.Figure()
colors = {"AAPL": "#3B82F6", "MSFT": "#00D68F", "NVDA": "#F5A623", "GOOGL": "#A78BFA", "AMZN": "#FF4757"}
for tkr in ["AAPL","MSFT","NVDA","GOOGL","AMZN"]:
    d = samples[samples['Ticker'] == tkr].sort_values('Date')
    base = d['Close'].iloc[0]
    indexed = d['Close'] / base * 100
    fig1.add_trace(go.Scatter(x=d['Date'], y=indexed, mode='lines', name=tkr,
                               line=dict(color=colors[tkr], width=2)))
fig1.update_layout(**base_layout("Indexed Price Performance — Big Tech (Jan 2010 = 100)", 480))
fig1.update_yaxes(title="Indexed Value")
figs['tech_performance'] = fig1

# ---- 2. Risk vs Return scatter (ticker_summary) ----
ts = pd.read_parquet('cleaned-data/ticker_summary.parquet')
ts_plot = ts[(ts['Annualized_Volatility'] < 1.5) & (ts['Annualized_Return'].abs() < 2)]
fig2 = px.scatter(
    ts_plot, x="Annualized_Volatility", y="Annualized_Return", color="AssetType",
    hover_data=["Ticker"], opacity=0.55,
    color_discrete_map={"Stock": BLUE, "ETF": AMBER},
)
fig2.update_traces(marker=dict(size=5))
fig2.add_hline(y=0, line_color=MUTED, line_width=1)
fig2.update_layout(**base_layout("Risk vs. Return — All Tickers (2015–2017)", 480))
fig2.update_xaxes(title="Annualized Volatility", tickformat=".0%")
fig2.update_yaxes(title="Annualized Return", tickformat=".0%")
figs['risk_return'] = fig2

# ---- 3. Top 20 Gainers bar ----
top_gainers = pd.read_excel('outputs/Stock_Market_Summary_Tables.xlsx', sheet_name='Top_20_Gainers')
top_gainers = top_gainers.sort_values("Total_Return")
fig3 = go.Figure(go.Bar(
    x=top_gainers['Total_Return'], y=top_gainers['Ticker'], orientation='h',
    marker=dict(color=GREEN),
    text=[f"{v:.0%}" for v in top_gainers['Total_Return']], textposition='outside',
    textfont=dict(color=TEXT, size=10),
))
fig3.update_layout(**base_layout("Top 20 Gainers, 2015–2017 (Total Return)", 560))
fig3.update_xaxes(title="Total Return", tickformat=".0%")
figs['top_gainers'] = fig3

# ---- 4. Market volume over time (stacked area) ----
ms = pd.read_parquet('cleaned-data/monthly_summary.parquet')
ms['Month'] = pd.to_datetime(ms['Month'])
fig4 = go.Figure()
for asset, color in [("Stock", BLUE), ("ETF", AMBER)]:
    d = ms[ms['AssetType'] == asset].sort_values('Month')
    fig4.add_trace(go.Scatter(x=d['Month'], y=d['Total_Volume'], mode='lines', name=asset,
                               stackgroup='one', line=dict(width=0.5, color=color),
                               fillcolor=color))
fig4.update_layout(**base_layout("Total Trading Volume by Month, 2010–2017", 440))
fig4.update_yaxes(title="Shares Traded")
figs['volume_trend'] = fig4

# ---- 5. Average volatility over time by asset type ----
fig5 = go.Figure()
for asset, color in [("Stock", BLUE), ("ETF", AMBER)]:
    d = ms[ms['AssetType'] == asset].sort_values('Month')
    fig5.add_trace(go.Scatter(x=d['Month'], y=d['Avg_Volatility'], mode='lines', name=asset,
                               line=dict(color=color, width=2)))
fig5.update_layout(**base_layout("Average 20-Day Volatility by Month", 420))
fig5.update_yaxes(title="Avg Volatility (annualized)", tickformat=".0%")
figs['volatility_trend'] = fig5

# ---- 6. Most liquid tickers ----
most_liquid = pd.read_excel('outputs/Stock_Market_Summary_Tables.xlsx', sheet_name='Most_Liquid')
most_liquid = most_liquid.sort_values("Avg_Daily_Volume")
fig6 = go.Figure(go.Bar(
    x=most_liquid['Avg_Daily_Volume'], y=most_liquid['Ticker'], orientation='h',
    marker=dict(color=[BLUE if a=="Stock" else AMBER for a in most_liquid['AssetType']]),
))
fig6.update_layout(**base_layout("Most Liquid Tickers by Avg Daily Volume, 2015–2017", 560))
fig6.update_xaxes(title="Avg Daily Volume (shares)")
figs['most_liquid'] = fig6

# ---- 7. Active tickers over time (market breadth) ----
fig7 = go.Figure()
for asset, color in [("Stock", BLUE), ("ETF", AMBER)]:
    d = ms[ms['AssetType'] == asset].sort_values('Month')
    fig7.add_trace(go.Scatter(x=d['Month'], y=d['Active_Tickers'], mode='lines', name=asset,
                               line=dict(color=color, width=2)))
fig7.update_layout(**base_layout("Market Breadth — Active Tickers per Month", 420))
fig7.update_yaxes(title="Active Tickers")
figs['breadth_trend'] = fig7

# Save each fig as HTML div
import plotly.io as pio
divs = {}
for name, fig in figs.items():
    divs[name] = pio.to_html(fig, full_html=False, include_plotlyjs=False, div_id=name)

with open('outputs/figures/divs.json', 'w') as f:
    json.dump(divs, f)

print("Saved", len(divs), "figure divs")
