
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime


st.set_page_config(layout="wide")


st.title("Portfolio Tracker")
st.sidebar.success("Open TradeNet from sidebar")


# Load CSV
df = pd.read_csv("portfolio.csv")

# Convert dates
df["Buy Date"] = pd.to_datetime(df["Buy Date"])

# -------------------------
# DATE FILTER
# -------------------------

min_date = df["Buy Date"].min()
max_date = df["Buy Date"].max()

date_range = st.date_input(
    "Filter by Date Range",
    [min_date, max_date]
)

if len(date_range) == 2:
    start_date, end_date = date_range

    df = df[
        (df["Buy Date"] >= pd.to_datetime(start_date)) &
        (df["Buy Date"] <= pd.to_datetime(end_date))
    ]

# -------------------------
# LIVE STOCK DATA
# -------------------------

live_prices = []

for stock in df["Stock"]:
    ticker = yf.Ticker(stock)

    try:
        current_price = ticker.history(period="1d")["Close"].iloc[-1]
    except:
        current_price = 0

    live_prices.append(current_price)

df["Current Price"] = live_prices

# -------------------------
# CALCULATIONS
# -------------------------

df["Investment"] = df["Quantity"] * df["Buy Price"]

df["Current Value"] = (
    df["Quantity"] * df["Current Price"]
)

df["P/L Amount"] = (
    df["Current Value"] - df["Investment"]
)

df["P/L %"] = (
    df["P/L Amount"] / df["Investment"]
) * 100

# -------------------------
# KPIs
# -------------------------

total_investment = df["Investment"].sum()
current_value = df["Current Value"].sum()
profit_loss = df["P/L Amount"].sum()

win_rate = (
    len(df[df["P/L Amount"] > 0]) / len(df)
) * 100

pl_percent = (
    profit_loss / total_investment
) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Investment",
    f"₹{total_investment:,.2f}"
)

col2.metric(
    "Current Value",
    f"₹{current_value:,.2f}",
    f"{profit_loss:,.2f}"
)

col3.metric(
    "Win Rate",
    f"{win_rate:.1f}%"
)

col4.metric(
    "Total P/L %",
    f"{pl_percent:.2f}%"
)

st.divider()

# -------------------------
# TOP 10 / ALL STOCKS
# -------------------------

view_option = st.selectbox(
    "Select Stocks View",
    ["Top 10 Stocks", "All Stocks"]
)

if view_option == "Top 10 Stocks":
    display_df = df.nlargest(10, "Investment")
else:
    display_df = df

# -------------------------
# DONUT CHARTS
# -------------------------

st.subheader("Asset Allocation")

col1, col2 = st.columns(2)

with col1:

    fig1 = px.pie(
        display_df,
        values="Investment",
        names="Stock",
        hole=0.5,
        title="Open"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with col2:

    profitable = display_df[
        display_df["P/L Amount"] > 0
    ]

    fig2 = px.pie(
        profitable,
        values="Current Value",
        names="Stock",
        hole=0.5,
        title="Realized"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

st.divider()

# -------------------------
# SEARCH FILTER
# -------------------------

# -------------------------
# ADVANCED FILTERS
# -------------------------

with st.expander("Filter Stocks"):

    selected_stocks = st.multiselect(
        "Filter Scripts",
        options=df["Stock"].unique(),
        default=[]
    )

    min_pl = float(df["P/L %"].min())
    max_pl = float(df["P/L %"].max())

    pl_range = st.slider(
       "P/L % Range",
        min_value=min_pl,
        max_value=max_pl,
        value=(min_pl, max_pl),
        step=1.0
   )

    min_price = float(df["Buy Price"].min())
    max_price = float(df["Buy Price"].max())

    buy_range = st.slider(
        "Buy Price Range",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=10.0
  )

# APPLY FILTERS

filtered_df = display_df.copy()

# Stock filter
if selected_stocks:
    filtered_df = filtered_df[
        filtered_df["Stock"].isin(selected_stocks)
    ]

# P/L filter
filtered_df = filtered_df[
    (filtered_df["P/L %"] >= pl_range[0]) &
    (filtered_df["P/L %"] <= pl_range[1])
]

# Buy price filter
filtered_df = filtered_df[
    (filtered_df["Buy Price"] >= buy_range[0]) &
    (filtered_df["Buy Price"] <= buy_range[1])
]
# -------------------------
# TABLE
# -------------------------

st.subheader("Portfolio Explorer")

st.dataframe(
    filtered_df.reset_index(drop=True),
    use_container_width=True
)