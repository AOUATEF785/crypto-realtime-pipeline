# 📈 Real-Time Crypto Analytics Pipeline & Dashboard

An End-to-End data engineering pipeline that streams real-time market data from the Binance WebSocket API, processes technical indicators on the fly, stores the data in a PostgreSQL database, and visualizes live updates on an interactive Streamlit dashboard.

## 🏗️ Architecture Architecture

- **Data Source:** Binance WebSocket API (BTC/USDT @kline_1m stream).
- **Ingestion & Processing:** Python script utilizing `websocket-client` and `pandas-ta` for real-time technical indicators calculations (SMA, RSI).
- **Storage:** PostgreSQL relational database optimized with chronological indexing.
- **Visualization:** Streamlit web application integrated with dynamic Plotly charts (Candlesticks & Line charts).

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Database:** PostgreSQL
- **Libraries:** `psycopg2-binary`, `websocket-client`, `pandas`, `pandas-ta`, `streamlit`, `plotly`

## 🚀 How to Run the Project

### 1. Prerequisites & Database Setup

Create a PostgreSQL database named `crypto_db` via pgAdmin or psql.

### 2. Install Dependencies

```bash
pip install websocket-client psycopg2-binary pandas pandas-ta streamlit plotly
```
