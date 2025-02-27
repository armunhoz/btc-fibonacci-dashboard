import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# Função para obter dados do BTC na Binance
def get_binance_data(symbol="BTCUSDT", interval="1d", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica se houve erro na requisição
        data = response.json()
        
        if not isinstance(data, list):  # Se a resposta não for uma lista, há erro
            st.error(f"Erro na resposta da Binance: {data}")
            return pd.DataFrame()
        
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"])
        
        # Corrigir timestamp correto
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        return df
    
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API da Binance: {e}")
        return pd.DataFrame()

# Função para calcular níveis de Fibonacci
def fibonacci_retracement(df):
    max_price = df["high"].max()
    min_price = df["low"].min()
    
    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    retracement_levels = [(max_price - (max_price - min_price) * level) for level in fib_levels]
    
    return retracement_levels, max_price, min_price, fib_levels

# Interface do Streamlit
st.title("📈 Análise de Fibonacci para BTC/USDT")

# Seleção de intervalo de tempo
interval = st.selectbox("Selecione o intervalo:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=5)

# Obter dados e calcular Fibonacci
df = get_binance_data(interval=interval)

if df.empty:
    st.error("Erro ao carregar os dados. Verifique se a API da Binance está disponível.")
else:
    st.write("### Dados Recebidos da Binance", df.head())  # Debug: Mostra os primeiros dados retornados
    retracements, max_price, min_price, fib_levels = fibonacci_retracement(df)

    # Criar gráfico com Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["close"], mode='lines', name='Preço BTC'))

    # Adicionar linhas de Fibonacci
    colors = ['red', 'orange', 'yellow', 'green', 'blue']
    for i, level in enumerate(retracements):
        fig.add_shape(type='line', x0=df["timestamp"].iloc[0], x1=df["timestamp"].iloc[-1], y0=level, y1=level, line=dict(color=colors[i], dash='dash'))
        fig.add_annotation(x=df["timestamp"].iloc[len(df)//2], y=level, text=f'Fib {fib_levels[i] * 100:.1f}%', showarrow=False, bgcolor=colors[i])

    fig.update_layout(title=f"Fibonacci Retracements ({interval})", xaxis_title="Tempo", yaxis_title="Preço (USDT)", template="plotly_dark")

    # Mostrar gráfico
    st.plotly_chart(fig)
