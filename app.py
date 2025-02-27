import streamlit as st
import pandas as pd
import requests
import time

# Interface do Streamlit
st.title("📈 Análise de Fibonacci para BTC/USD com TradingView")

# Opções de tempo gráfico
timeframe = st.selectbox("Escolha o período do gráfico:", ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"], index=5)

# Código HTML para incorporar o widget do TradingView
tv_widget = f'''
    <iframe src="https://s.tradingview.com/embed-widget/advanced-chart/?symbol=BINANCE:BTCUSDT&interval={timeframe}&theme=dark&style=1&locale=br&toolbarbg=f1f3f6&hide_top_toolbar=false&hide_side_toolbar=false&allow_symbol_change=true&save_image=true" 
    width="100%" height="600" frameborder="0" allowfullscreen></iframe>
'''

# Exibir o gráfico do TradingView
st.markdown(tv_widget, unsafe_allow_html=True)
