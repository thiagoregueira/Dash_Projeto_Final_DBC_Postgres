import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from etl.cambio import obter_variacao_cambio, baixar_historico_cambio
from style.style_config import apply_custom_style, COLORS, add_footer

# Aplicar estilo customizado
apply_custom_style()

st.title("Câmbio em relação ao real(R$)")

# # Verifica se o arquivo histórico existe, se não, baixa os dados
# if not pd.io.common.file_exists('../results/historico_cambio.csv'):
#     st.warning('Baixando histórico do câmbio... Isso pode levar alguns minutos.')
#     baixar_historico_cambio()

# Obter caminho absoluto para o arquivo
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
historico_path = os.path.join(base_path, "results", "historico_cambio.csv")

# Carregar dados históricos
df_cambio = pd.read_csv(historico_path)

# Variável para armazenar o período selecionado
if "periodo_analise" not in st.session_state:
    st.session_state.periodo_analise = "1y"

# Criar dicionário de moedas (Nome -> Símbolo)
moedas_dict = df_cambio.groupby('Nome_Moeda')['Simbolo'].first().to_dict()

# Campo de seleção da moeda usando o nome
nome_moeda_selecionada = st.selectbox("Selecione uma moeda:", list(moedas_dict.keys()))

# Obter o símbolo correspondente ao nome selecionado
moeda_selecionada = moedas_dict[nome_moeda_selecionada]

# Botões para selecionar período de análise
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("30 Dias"):
        st.session_state.periodo_analise = "1d"
with col2:
    if st.button("Mensal"):
        st.session_state.periodo_analise = "1mo"
with col3:
    if st.button("Anual"):
        st.session_state.periodo_analise = "1y"

# Filtrar dados da moeda selecionada
dados_moeda = df_cambio[df_cambio["Simbolo"] == moeda_selecionada].copy()
dados_moeda["Data"] = pd.to_datetime(dados_moeda["Data"])
dados_moeda = dados_moeda.sort_values("Data")

# Filtrar por período e criar gráfico
data_atual = pd.to_datetime(dados_moeda["Data"].max())
if st.session_state.periodo_analise == "1d":
    data_inicio = data_atual - timedelta(days=30)
    titulo_periodo = "Últimos 30 dias"
elif st.session_state.periodo_analise == "1mo":
    data_inicio = data_atual - timedelta(days=30 * 12)  # Último ano por mês
    titulo_periodo = "Variação Mensal"
else:  # '1y'
    data_inicio = data_atual - timedelta(days=365 * 3)  # Últimos 3 anos
    titulo_periodo = "Variação Anual"

dados_moeda = dados_moeda[dados_moeda["Data"] >= data_inicio]
dados_moeda = dados_moeda.set_index("Data")

# Plotar gráfico de linha
nome_moeda = (
    dados_moeda["Nome_Moeda"].iloc[0] if not dados_moeda.empty else moeda_selecionada
)
st.subheader(f"Evolução do Preço - {nome_moeda} ({titulo_periodo})")

if not dados_moeda.empty:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dados_moeda.index,
            y=dados_moeda["Preco"],
            mode="lines",
            name="Preço",
            line=dict(color=COLORS["primary"]),
        )
    )
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        showlegend=True,
        plot_bgcolor=COLORS["background_graph"],
        paper_bgcolor=COLORS["background_graph"],
        font=dict(color=COLORS["text"]),
        xaxis=dict(gridcolor=COLORS["dark_blue"], zerolinecolor=COLORS["dark_blue"]),
        yaxis=dict(gridcolor=COLORS["dark_blue"], zerolinecolor=COLORS["dark_blue"]),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Exibir informações adicionais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Preço Atual",
            value=f"R$ {dados_moeda['Preco'].iloc[-1]:.2f}",
            delta=f"{dados_moeda['Variacao'].iloc[-1]:.2f}%",
        )
    with col2:
        st.metric(label="Preço Máximo", value=f"R$ {dados_moeda['Preco'].max():.2f}")
    with col3:
        st.metric(label="Preço Mínimo", value=f"R$ {dados_moeda['Preco'].min():.2f}")

    st.info(
        f"Período: {dados_moeda.index[0].strftime('%d/%m/%Y')} até {dados_moeda.index[-1].strftime('%d/%m/%Y')}"
    )
else:
    st.warning("Não há dados disponíveis para esta moeda no período selecionado.")

# Obter variação das moedas
variacoes = obter_variacao_cambio(st.session_state.periodo_analise)

if not variacoes.empty:
    st.subheader(f"Variação das Moedas ({titulo_periodo})")

    # Definir a ordem desejada para a primeira coluna
    primeira_coluna = ["Dólar Americano", "Euro", "Libra Esterlina"]

    # Separar as moedas da primeira coluna
    moedas_primeira_coluna = variacoes[variacoes["Nome"].isin(primeira_coluna)]
    # Ordenar conforme a ordem desejada
    moedas_primeira_coluna = (
        moedas_primeira_coluna.set_index("Nome").loc[primeira_coluna].reset_index()
    )

    # Pegar as demais moedas
    outras_moedas = variacoes[~variacoes["Nome"].isin(primeira_coluna)]

    # Criar colunas
    col1, col2, col3 = st.columns(3)

    # Primeira coluna - Moedas principais
    with col1:
        for _, moeda in moedas_primeira_coluna.iterrows():
            st.metric(
                label=f"{moeda['Nome']}",
                value=f"R$ {moeda['Preço']:.2f}",
                delta=f"{moeda['Variação (%)']}%",
            )

    # Dividir as outras moedas entre as duas colunas restantes
    metade = len(outras_moedas) // 2

    # Segunda coluna
    with col2:
        for _, moeda in outras_moedas.iloc[:metade].iterrows():
            st.metric(
                label=f"{moeda['Nome']}",
                value=f"R$ {moeda['Preço']:.2f}",
                delta=f"{moeda['Variação (%)']}%",
            )

    # Terceira coluna
    with col3:
        for _, moeda in outras_moedas.iloc[metade:].iterrows():
            st.metric(
                label=f"{moeda['Nome']}",
                value=f"R$ {moeda['Preço']:.2f}",
                delta=f"{moeda['Variação (%)']}%",
            )
else:
    st.warning("Não há dados disponíveis.")

# Adicionar footer padronizado
add_footer()
