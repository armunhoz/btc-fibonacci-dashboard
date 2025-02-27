import os
os.system("pip install yfinance")

import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

# Função para obter dados do BTC via Yahoo Finance
@st.cache_data(ttl=600)  # Cache válido por 10 minutos
def get_yahoo_data(symbol="BTC-USD", interval="1h", period="30d"):
    try:
        df = yf.download(symbol, interval=interval, period=period)
        df.reset_index(inplace=True)
        df.rename(columns={"Date": "timestamp", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a API do Yahoo Finance: {e}")
        return pd.DataFrame()

# Função de IA para gerar sinais de compra/venda
def generate_trading_signals(df):
    if "close" not in df.columns:
        st.error("Erro: Dados não carregados corretamente. Verifique a fonte de dados.")
        return df
    
    df["sma_50"] = df["close"].rolling(window=50).mean()
    df["sma_200"] = df["close"].rolling(window=200).mean()
    
    # Gerar sinais de compra e venda
    df["signal"] = np.where(df["sma_50"] > df["sma_200"], "Compra", "Venda")
    df.dropna(inplace=True)
    return df

# Interface do Streamlit
st.title("📈 Análise de Fibonacci e IA para BTC/USD")

# Opções de tempo gráfico
timeframe = st.selectbox("Escolha o período do gráfico:", ["1h", "4h", "1d", "1wk"], index=0)

# Obter dados do Yahoo Finance
df = get_yahoo_data(interval=timeframe)
df = generate_trading_signals(df)

if df.empty:
    st.error("Erro ao carregar os dados. Verifique se a API do Yahoo Finance está disponível.")
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
