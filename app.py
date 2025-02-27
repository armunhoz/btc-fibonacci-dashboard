import streamlit as st
import pandas as pd
import requests
import time

# Interface do Streamlit
st.title("📈 Análise de Fibonacci para BTC/USD com TradingView")

# Opções de tempo gráfico
timeframe = st.selectbox("Escolha o período do gráfico:", ["1", "5", "15", "60", "240", "1D", "1W", "1M"], index=5)

# Código HTML para incorporar o widget completo do TradingView
tv_widget = f'''
    <div class="tradingview-widget-container" style="width: 1920px; max-width: 100%; height: 800px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
            new TradingView.widget({{
                "width": "100%",
                "height": 800,
                "symbol": "BINANCE:BTCUSDT",
                "interval": "{timeframe}",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "br",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_top_toolbar": false,
                "hide_legend": false,
                "allow_symbol_change": true,
                "show_popup_button": true,
                "popup_width": "1000",
                "popup_height": "650",
                "studies": [
                    "RSI@tv-basicstudies",
                    "MACD@tv-basicstudies",
                    "MAExp@tv-basicstudies"
                ],
                "container_id": "tradingview_chart"
            }});
        </script>
    </div>
'''

# Exibir o gráfico do TradingView
st.markdown(tv_widget, unsafe_allow_html=True)
