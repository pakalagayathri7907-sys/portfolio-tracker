import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Portfolio Tracker")

# Load portfolio
df = pd.read_csv("portfolio.csv")

# Live prices
live_prices = []

for stock in df["Stock"]:
    ticker = yf.Ticker(stock)
    try:
        price = ticker.history(period="1d")["Close"].iloc[-1]
    except:
        price = 0
    live_prices.append(price)

df["Current Price"] = live_prices

# Calculations
df["Investment"] = df["Quantity"] * df["Buy Price"]
df["Current Value"] = df["Quantity"] * df["Current Price"]
df["P/L Amount"] = df["Current Value"] - df["Investment"]

df["P/L %"] = (
    (df["P/L Amount"] / df["Investment"]) * 100
)

# KPIs
total_investment = df["Investment"].sum()
current_value = df["Current Value"].sum()
profit_loss = df["P/L Amount"].sum()

win_rate = (
    (df["P/L Amount"] > 0).mean() * 100
)

# KPI Row
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
    f"{(profit_loss/total_investment)*100:.2f}%"
)

st.divider()

# Charts
col5, col6 = st.columns(2)

fig1 = px.pie(
    df,
    names="Stock",
    values="Current Value",
    title="Asset Allocation"
)

col5.plotly_chart(fig1, use_container_width=True)

profit_df = df[df["P/L Amount"] > 0]

fig2 = px.pie(
    profit_df,
    names="Stock",
    values="P/L Amount",
    title="Profitable Stocks"
)

col6.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("Portfolio Explorer")

st.dataframe(
    df,
    use_container_width=True
)