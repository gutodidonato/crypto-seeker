import pandas as pd
import streamlit as st
import yfinance as yf
import cryptocompare
import plotly.graph_objs as go
from datetime import datetime

# Inicialização do estado
if "assets" not in st.session_state:
    st.session_state.assets = []

# Função para obter dados de ações
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        agora = datetime.now()
        hist = stock.history(period="1d", start="2024-01-01", end=agora)
        return hist
    except Exception as e:
        st.error(f"Erro ao obter dados da ação {ticker}: {e}")
        return None

# Função para obter dados de criptomoedas
def get_crypto_data(crypto):
    try:
        data = cryptocompare.get_historical_price_day(crypto, currency='BRL', limit=365 * 4)
        if data:
            for day in data:
                day['time'] = datetime.fromtimestamp(day['time']).date()  # Formatar datas
        return data
    except Exception as e:
        st.error(f"Erro ao obter dados da criptomoeda {crypto}: {e}")
        return None

# Título do aplicativo
st.title("📊 Acompanhamento de Criptomoedas e Ações")

# Sidebar para seleção de tipo de ativo
st.sidebar.header("Selecione o tipo de ativo")
option = st.sidebar.selectbox(
    'Escolha o tipo de ativo',
    ('Ações', 'Criptomoedas')
)

# Entrada de dados e adição ao estado
if option == 'Ações':
    ticker = st.sidebar.text_input('Digite o ticker da ação (ex: AAPL, MSFT, GOOGL):')
    if st.sidebar.button("Adicionar Ação"):
        if ticker:
            data = get_stock_data(ticker)
            if data is not None and not data.empty:
                st.session_state.assets.append((ticker, data, 'Ação'))
                st.success(f"Ação {ticker} adicionada.")
            else:
                st.warning("Dados não disponíveis para a ação selecionada.")
elif option == 'Criptomoedas':
    crypto = st.sidebar.text_input('Digite o símbolo da criptomoeda (ex: BTC, ETH, DOGE):')
    if st.sidebar.button("Adicionar Criptomoeda"):
        if crypto:
            data = get_crypto_data(crypto)
            if data:
                st.session_state.assets.append((crypto, data, 'Criptomoeda'))
                st.success(f"Criptomoeda {crypto} adicionada.")
            else:
                st.warning("Dados não disponíveis para a criptomoeda selecionada.")

# Gráfico
st.header("📈 Desempenho dos Ativos")
fig = go.Figure()

for asset in st.session_state.assets:
    name, data, asset_type = asset
    if asset_type == 'Ação':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=name))
    elif asset_type == 'Criptomoeda':
        prices = [day['close'] for day in data]
        dates = [day['time'] for day in data]
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name=name))

if st.session_state.assets:
    fig.update_layout(title="Desempenho dos Ativos", xaxis_title="Data", yaxis_title="Preço", template="plotly_dark")
    st.plotly_chart(fig)
else:
    st.write("Adicione ativos para visualizar o desempenho.")

# Detalhamento dos ativos
st.header("📋 Detalhes dos Ativos")
for asset in st.session_state.assets:
    name, data, asset_type = asset
    st.subheader(f"{asset_type}: {name}")
    if asset_type == 'Ação':
        st.dataframe(data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10))
    elif asset_type == 'Criptomoeda':
        st.dataframe(pd.DataFrame(data).tail(10))
