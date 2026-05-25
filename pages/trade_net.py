import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# PAGE SETTINGS
st.set_page_config(layout="wide")

# SIDEBAR
st.sidebar.title("TradeNet")

st.sidebar.metric("Advances", 6)
st.sidebar.metric("Declines", 8)
st.sidebar.metric("Neutral", 16)

indicator = st.sidebar.selectbox(
    "Standard Indicators",
    ["RSI", "MACD", "VWAP"]
)

moving_avg = st.sidebar.selectbox(
    "Moving Average",
    ["20 EMA", "50 EMA", "200 EMA"]
)

bollinger = st.sidebar.selectbox(
    "Bollinger Bands",
    ["Upper", "Lower"]
)

# TITLE
st.title("Live Fishing Net for Trade Opportunities")

# STOCK LIST
stocks = [
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "TCS.NS",
    "SBIN.NS",
    "LT.NS",
    "ITC.NS",
    "WIPRO.NS",
    "MARUTI.NS"
]

# DROPDOWNS
col1, col2, col3 = st.columns(3)

with col1:
    stock = st.selectbox(
        "Select a Symbol",
        stocks
    )

with col2:
    interval = st.selectbox(
        "Interval",
        ["5m", "15m", "1h", "1d"]
    )

with col3:
    period = st.selectbox(
        "Period",
        ["1d", "5d", "1mo"]
    )

# BUTTON
if st.button("Go"):

    # DOWNLOAD DATA
    data = yf.download(
        stock,
        period=period,
        interval=interval,
        auto_adjust=True
    )

    # CHECK EMPTY
    if data.empty:
        st.error("No data found")

    else:

        # MOVING AVERAGES
        data["20 EMA"] = data["Close"].ewm(span=20).mean()
        data["50 EMA"] = data["Close"].ewm(span=50).mean()

        # SUPPORT / RESISTANCE
        support = data["Low"].min().min()
        resistance = data["High"].max().max()

        # PIVOT
        pivot = (
            data["High"].mean().mean() +
            data["Low"].mean().mean() +
            data["Close"].mean().mean()
        ) / 3

        # CHART
        fig = go.Figure()

        # CANDLESTICK
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'].values.flatten(),
                high=data['High'].values.flatten(),
                low=data['Low'].values.flatten(),
                close=data['Close'].values.flatten(),
                name='Candlestick'
            )
        )

        # EMA LINE
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["20 EMA"],
                mode="lines",
                name="20 EMA",
                line=dict(color="blue")
            )
        )

        # SUPPORT LINE
        fig.add_hline(
            y=support,
            line_dash="dot",
            line_color="green"
        )

        # RESISTANCE LINE
        fig.add_hline(
            y=resistance,
            line_dash="dot",
            line_color="red"
        )

        # PIVOT LINE
        fig.add_hline(
            y=pivot,
            line_dash="dash",
            line_color="orange"
        )

        # BREAKDOWN SIGNALS
        breakdown = data[data["Close"] < pivot]

        fig.add_trace(
            go.Scatter(
                x=breakdown.index,
                y=breakdown["Low"],
                mode="markers+text",
                text=breakdown["Low"].round(2),
                textposition="bottom center",
                marker=dict(
                    color="red",
                    size=12,
                    symbol="triangle-down"
                ),
                hovertemplate=
                "<b>BREAKDOWN</b><br>" +
                "Price: %{y}<br>" +
                "Time: %{x}<extra></extra>",
                name="Breakdown"
            )
        )

        # LAYOUT
        fig.update_layout(
            height=850,
            xaxis_rangeslider_visible=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",

            xaxis=dict(
                title="Date",
                showgrid=True,
                gridcolor="lightgray"
            ),

            yaxis=dict(
                title="Price",
                side="right",
                showgrid=True,
                gridcolor="lightgray"
            )
        )

        # SHOW CHART
        st.plotly_chart(
            fig,
            use_container_width=True
        )