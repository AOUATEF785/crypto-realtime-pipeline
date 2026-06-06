import streamlit as st
import psycopg2
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 🛠️ Configuration dyal l-PostgreSQL (Nfs params li f ingest_data.py)
DB_PARAMS = {
    "dbname": "crypto_db",
    "user": "postgres",
    "password": "123",  # 👈 Rah m9add standard b admin dbâ
    "host": "localhost",
    "port": "5432"
}

st.set_page_config(page_title="Crypto Real-Time Dashboard", layout="wide")

st.title("📈 BTC/USDT Real-Time Analytics Dashboard")
st.write("Live data streamed from Binance WebSockets into PostgreSQL")

def load_data():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        query = "SELECT * FROM market_data ORDER BY timestamp DESC LIMIT 100;"
        df = pd.read_sql(query, conn)
        conn.close()
        # Sort values by timestamp for correct line plotting
        if not df.empty:
            df = df.sort_values('timestamp')
        return df
    except Exception as e:
        st.error(f"❌ Error fetching from Database: {e}")
        return pd.DataFrame()

# Load real-time data
df = load_data()

if df.empty:
    st.warning("⏳ Database is currently empty or connecting... Waiting for data from ingest_data.py (Allow 1-2 mins).")
else:
    # Live Metric Cards
    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"${float(latest['close_price']):,.2f}")
    col2.metric("Volume", f"{float(latest['volume']):,.2f}")
    col3.metric("RSI (14)", f"{float(latest['rsi_14']):.2f}" if latest['rsi_14'] else "Calculating...")
    col4.metric("SMA (20)", f"${float(latest['sma_20']):,.2f}" if latest['sma_20'] else "Calculating...")

    st.markdown("---")

    # Interactive Candlestick Chart with SMA
    st.subheader("📊 Bitcoin Live Price Action & Technical Indicators")
    fig = go.Figure()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open_price'],
        high=df['high_price'],
        low=df['low_price'],
        close=df['close_price'],
        name="Candlestick"
    ))

    # Add SMA Line if available
    if 'sma_20' in df.columns and not df['sma_20'].isna().all():
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['sma_20'], 
            mode='lines', 
            line=dict(color='orange', width=2), 
            name='SMA 20'
        ))

    fig.update_layout(xaxis_rangeslider_visible=False, height=500, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # RSI Section
    if 'rsi_14' in df.columns and not df['rsi_14'].isna().all():
        st.subheader("📉 Relative Strength Index (RSI)")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi_14'], mode='lines', line=dict(color='purple', width=2), name='RSI'))
        
        # Overbought / Oversold Lines
        fig_rsi.add_shape(type="line", x0=df['timestamp'].min(), y0=70, x1=df['timestamp'].max(), y1=70, line=dict(color="red", dash="dash"))
        fig_rsi.add_shape(type="line", x0=df['timestamp'].min(), y0=30, x1=df['timestamp'].max(), y1=30, line=dict(color="green", dash="dash"))
        
        fig_rsi.update_layout(yaxis=dict(range=[0, 100]), height=250, template="plotly_dark")
        st.plotly_chart(fig_rsi, use_container_width=True)

    # Raw Data Table
    st.subheader("📋 Recent Market Data Records")
    st.dataframe(df.tail(10)[['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']].sort_values('timestamp', ascending=False), use_container_width=True)

# Auto refresh functionality
st.caption("Auto-updates every minute as new candles close on Binance.")