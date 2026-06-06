import websocket
import json
import psycopg2
from datetime import datetime, timezone
import pandas as pd
import pandas_ta as ta
from collections import deque

# Configuration dyal l-PostgreSQL dyalk
DB_PARAMS = {
    "dbname": "crypto_db",
    "user": "postgres",
    "password": "123",  # ⚠️ Beddel hada b l-password dyal PostgreSQL dyalk
    "host": "localhost",
    "port": "5432"
}

def init_db():
    """Kat-gadd l-table f PostgreSQL direct mn Python ila makantsh."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            symbol VARCHAR(10) NOT NULL,
            open_price NUMERIC(18, 4),
            high_price NUMERIC(18, 4),
            low_price NUMERIC(18, 4),
            close_price NUMERIC(18, 4),
            volume NUMERIC(18, 4),
            sma_20 NUMERIC(18, 4),
            rsi_14 NUMERIC(18, 4)
        );
        CREATE INDEX IF NOT EXISTS idx_timestamp ON market_data (timestamp DESC);
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("📁 Database & Table initialized successfully!")
    except Exception as e:
        clean_error = str(e).encode('utf-8', errors='ignore').decode('utf-8')
        print(f"❌ Initialization Error: {clean_error}")

def insert_to_db(data):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        query = """
        INSERT INTO market_data (timestamp, symbol, open_price, high_price, low_price, close_price, volume, sma_20, rsi_14)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        cur.execute(query, (
            data['timestamp'], data['symbol'], data['open'], data['high'], 
            data['low'], data['close'], data['volume'], data['sma_20'], data['rsi_14']
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        clean_error = str(e).encode('utf-8', errors='ignore').decode('utf-8')
        print(f"❌ Database Insertion Error: {clean_error}")

# Fixed-size list f l-memory (max 50 rows)
history = deque(maxlen=50)

def on_message(ws, message):
    raw_data = json.loads(message)
    candle = raw_data['k']
    
    is_candle_closed = candle['x'] 
    
    current_candle = {
        'timestamp': datetime.fromtimestamp(candle['t'] / 1000, tz=timezone.utc),
        'symbol': raw_data['s'],
        'open': float(candle['o']),
        'high': float(candle['h']),
        'low': float(candle['l']),
        'close': float(candle['c']),
        'volume': float(candle['v']),
        'sma_20': None,
        'rsi_14': None
    }
    
    if is_candle_closed:
        history.append(current_candle)
        
        if len(history) >= 20:
            df = pd.DataFrame(list(history))
            df['sma_20'] = ta.sma(df['close'], length=20)
            df['rsi_14'] = ta.rsi(df['close'], length=14)
            
            current_candle['sma_20'] = float(df['sma_20'].iloc[-1]) if not pd.isna(df['sma_20'].iloc[-1]) else None
            current_candle['rsi_14'] = float(df['rsi_14'].iloc[-1]) if not pd.isna(df['rsi_14'].iloc[-1]) else None
            
        insert_to_db(current_candle)
        print(f"✅ Stored in Postgres: {current_candle['timestamp']} | Price: {current_candle['close']} | RSI: {current_candle['rsi_14']}")

def on_error(ws, error):
    print(f"❌ Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("🔌 Connection closed, reconnecting...")

if __name__ == "__main__":
    try:
        init_db()
        socket_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
        ws = websocket.WebSocketApp(socket_url, on_message=on_message, on_error=on_error, on_close=on_close)
        print("🚀 Production Pipeline started. Listening to Binance WebSockets...")
        ws.run_forever()
    except Exception as main_error:
        print(f"❌ CRITICAL ERROR: {main_error}")