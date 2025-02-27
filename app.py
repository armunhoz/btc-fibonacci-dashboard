import streamlit as st
import pandas as pd
import requests
import time
import numpy as np
import plotly.graph_objects as go

# Função para obter dados do BTC na CoinGecko com cache otimizado
@st.cache_data(ttl=600)  # Cache válido por 10 minutos
def get_coingecko_data(days=30, interval='hourly'):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}&interval={interval}"
    wait_time = 5  # Tempo inicial de espera
    
    for _ in range(5):  # Tentar até 5 vezes caso a API falhe
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "prices" not in data:
                st.error(f"Erro na resposta da CoinGecko: {data}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data["prices"], columns=["timestamp", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["open"] = df["close"].shift(1)
            df["high"] = df["close"].rolling(2).max()
            df["low"] = df["close"].rolling(2).min()
            df.dropna(inplace=True)
            return df
        
        except requests.exceptions.RequestException as e:
            st.warning(f"Tentativa falhou: {e}. Aguardando {wait_time} segundos...")
            time.sleep(wait_time)  # Aguardar antes de tentar novamente
            wait_time *= 2  # Aumentar o tempo de espera exponencialmente
    
    st.error("Erro ao conectar com a API da CoinGecko após múltiplas tentativas.")
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
timeframe = st.selectbox("Escolha o período do gráfico:", ["1", "5", "15", "60", "240", "1D", "1W", "1M"], index=5)

# Obter dados e gerar sinais
df = get_coingecko_data(days=30, interval="hourly")
df = generate_trading_signals(df)

if df.empty:
    st.error("Erro ao carregar os dados. Verifique se a API da CoinGecko está disponível.")
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
