import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# Função para obter dados do BTC na CoinGecko
def get_coingecko_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30&interval=daily"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "prices" not in data or "market_caps" not in data or "total_volumes" not in data:
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
        st.error(f"Erro ao conectar com a API da CoinGecko: {e}")
        return pd.DataFrame()

# Função para calcular níveis de Fibonacci
def fibonacci_retracement(df):
    max_price = df["high"].max()
    min_price = df["low"].min()
    
    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    retracement_levels = [(max_price - (max_price - min_price) * level) for level in fib_levels]
    
    return retracement_levels, max_price, min_price, fib_levels

# Interface do Streamlit
st.title("📈 Análise de Fibonacci para BTC/USD")

# Obter dados e calcular Fibonacci
df = get_coingecko_data()

if df.empty:
    st.error("Erro ao carregar os dados. Verifique se a API da CoinGecko está disponível.")
else:
    st.write("### Dados Recebidos da CoinGecko", df.head())
    retracements, max_price, min_price, fib_levels = fibonacci_retracement(df)

    # Criar gráfico com Plotly
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='Candlestick BTC'
    ))

    # Adicionar linhas de Fibonacci
    colors = ['red', 'orange', 'yellow', 'green', 'blue']
    for i, level in enumerate(retracements):
        fig.add_shape(type='line', x0=df["timestamp"].iloc[0], x1=df["timestamp"].iloc[-1], y0=level, y1=level, line=dict(color=colors[i], dash='dash'))
        fig.add_annotation(x=df["timestamp"].iloc[len(df)//2], y=level, text=f'Fib {fib_levels[i] * 100:.1f}%', showarrow=False, bgcolor=colors[i])

    fig.update_layout(title=f"Fibonacci Retracements BTC/USD", xaxis_title="Tempo", yaxis_title="Preço (USD)", template="plotly_dark")

    # Mostrar gráfico
    st.plotly_chart(fig)
