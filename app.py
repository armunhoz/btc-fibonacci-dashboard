import streamlit as st
import pandas as pd
import requests
import time
import numpy as np
import plotly.graph_objects as go

# Função para obter dados do BTC na Binance
@st.cache_data(ttl=600)  # Cache válido por 10 minutos
def get_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        return df
    
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API da Binance: {e}")
        return pd.DataFrame()

# Função de IA para gerar sinais de compra/venda
def generate_trading_signals(df):
    df["sma_50"] = df["close"].rolling(window=50).mean()
    df["sma_200"] = df["close"].rolling(window=200).mean()
    
    # Gerar sinais de compra e venda
    df["signal"] = np.where(df["sma_50"] > df["sma_200"], "Compra", "Venda")
    df.dropna(inplace=True)
    return df

# Interface do Streamlit
st.title("📈 Análise de Fibonacci e IA para BTC/USD")

# Opções de tempo gráfico
timeframe = st.selectbox("Escolha o período do gráfico:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)

# Obter dados da Binance
df = get_binance_data(interval=timeframe)
df = generate_trading_signals(df)

if df.empty:
    st.error("Erro ao carregar os dados. Verifique se a API da Binance está disponível.")
else:
    st.write("### 📊 Dados Processados com IA", df.tail())
    
    st.write("🔹 **Regras de Entrada e Saída**")
    st.write("✅ **Compra:** Quando SMA 50 cruza acima da SMA 200 (Golden Cross)")
    st.write("❌ **Venda:** Quando SMA 50 cruza abaixo da SMA 200 (Death Cross)")

    # Criar gráfico com sinais de compra/venda
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color='lime',
        decreasing_line_color='red',
        name='Candlestick BTC'
    ))

    # Adicionar sinais de compra/venda
    buy_signals = df[df["signal"] == "Compra"]
    sell_signals = df[df["signal"] == "Venda"]
    
    fig.add_trace(go.Scatter(
        x=buy_signals["timestamp"],
        y=buy_signals["close"],
        mode='markers',
        marker=dict(color='green', size=10, symbol='triangle-up'),
        name='Sinal de Compra'
    ))
    
    fig.add_trace(go.Scatter(
        x=sell_signals["timestamp"],
        y=sell_signals["close"],
        mode='markers',
        marker=dict(color='red', size=10, symbol='triangle-down'),
        name='Sinal de Venda'
    ))
    
    fig.update_layout(title="BTC/USD - Sinais de IA", xaxis_title="Tempo", yaxis_title="Preço (USD)", template="plotly_dark")
    
    # Mostrar gráfico
    st.plotly_chart(fig)
