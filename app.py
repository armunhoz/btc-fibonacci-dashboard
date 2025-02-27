import streamlit as st
import pandas as pd
import requests
import time

# Interface do Streamlit
st.title("📈 Análise de Fibonacci para BTC/USD com TradingView")

# Opções de tempo gráfico
timeframe = st.selectbox("Escolha o período do gráfico:", ["1", "5", "15", "60", "240", "1D", "1W", "1M"], index=5)

# Código HTML para incorporar o TradingView corretamente
tv_widget = f'''
    <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_{timeframe}&symbol=BINANCE:BTCUSDT&interval={timeframe}&theme=dark&style=1&locale=br&toolbarbg=f1f3f6&hide_top_toolbar=false&hide_side_toolbar=false&allow_symbol_change=true&save_image=true"
    width="100%" height="800" frameborder="0" allowfullscreen></iframe>
'''

# Exibir o gráfico do TradingView
st.markdown(tv_widget, unsafe_allow_html=True)
