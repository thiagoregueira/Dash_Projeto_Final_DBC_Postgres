import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
from etl.acoes import obter_melhores_e_piores_acoes, baixar_historico_acoes
from style.style_config import apply_custom_style, COLORS, add_footer

# Aplicar estilo customizado
apply_custom_style()

st.title("Ações Brasileiras")

# Obter caminho absoluto para o arquivo
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
historico_path = os.path.join(base_path, 'results', 'historico_acoes.csv')

# Carregar dados históricos
df_acoes = pd.read_csv(historico_path)

# Variável para armazenar o período selecionado
if 'periodo_analise' not in st.session_state:
    st.session_state.periodo_analise = '1y'

# Carregar lista de ações únicas
acoes = df_acoes['Simbolo'].unique().tolist()

# Campo de seleção da ação
acao_selecionada = st.selectbox('Selecione uma ação:', acoes)

# Botões para selecionar período de análise
col1, col2, col3 = st.columns(3)
with col1:
    if st.button('30 Dias'):
        st.session_state.periodo_analise = '1d'
with col2:
    if st.button('Mensal'):
        st.session_state.periodo_analise = '1mo'
with col3:
    if st.button('Anual'):
        st.session_state.periodo_analise = '1y'

# Filtrar dados da ação selecionada
dados_acao = df_acoes[df_acoes['Simbolo'] == acao_selecionada].copy()
dados_acao['Data'] = pd.to_datetime(dados_acao['Data'])
dados_acao = dados_acao.sort_values('Data')

# Filtrar por período e criar gráfico
data_atual = pd.to_datetime(dados_acao['Data'].max())
if st.session_state.periodo_analise == '1d':
    data_inicio = data_atual - timedelta(days=30)
    titulo_periodo = 'Últimos 30 dias'
elif st.session_state.periodo_analise == '1mo':
    data_inicio = data_atual - timedelta(days=30 * 12)
    titulo_periodo = 'Variação Mensal'
else:
    data_inicio = data_atual - timedelta(days=365 * 3)
    titulo_periodo = 'Variação Anual'

dados_acao = dados_acao[dados_acao['Data'] >= data_inicio]
dados_acao = dados_acao.set_index('Data')

# Plotar gráfico de linha
st.subheader(f'Evolução do Preço - {acao_selecionada} ({titulo_periodo})')
if not dados_acao.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dados_acao.index,
        y=dados_acao['Preco'],
        mode='lines',
        name='Preço',
        line=dict(color=COLORS['primary'])
    ))
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Preço (R$)',
        showlegend=True,
        plot_bgcolor=COLORS['background_graph'],
        paper_bgcolor=COLORS['background_graph'],
        font=dict(color=COLORS['text']),
        xaxis=dict(
            gridcolor=COLORS['dark_blue'],
            zerolinecolor=COLORS['dark_blue']
        ),
        yaxis=dict(
            gridcolor=COLORS['dark_blue'],
            zerolinecolor=COLORS['dark_blue']
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Exibir informações adicionais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Preço Atual",
            value=f"R$ {dados_acao['Preco'].iloc[-1]:.2f}",
            delta=f"{dados_acao['Variacao'].iloc[-1]:.2f}%"
        )
    with col2:
        st.metric(
            label="Preço Máximo",
            value=f"R$ {dados_acao['Preco'].max():.2f}"
        )
    with col3:
        st.metric(
            label="Preço Mínimo",
            value=f"R$ {dados_acao['Preco'].min():.2f}"
        )
    
    st.info(f'Período: {dados_acao.index[0].strftime("%d/%m/%Y")} até {dados_acao.index[-1].strftime("%d/%m/%Y")}')
else:
    st.warning('Não há dados disponíveis para esta ação no período selecionado.')

# Obter melhores e piores ações
melhores, piores = obter_melhores_e_piores_acoes(st.session_state.periodo_analise)

# Exibir cards de melhores e piores desempenhos
col1, col2 = st.columns(2)

with col1:
    st.subheader(f'Top 5 - Melhores Ações ({titulo_periodo})')
    if not melhores.empty:
        for _, acao in melhores.iterrows():
            st.metric(
                label=f"{acao['Símbolo']} - {acao['Empresa']}",
                value=f"R$ {acao['Preço']:.2f}",
                delta=f"{acao['Variação (%)']}%"
            )
    else:
        st.warning('Não há dados disponíveis.')

with col2:
    st.subheader(f'Top 5 - Piores Ações ({titulo_periodo})')
    if not piores.empty:
        for _, acao in piores.iterrows():
            st.metric(
                label=f"{acao['Símbolo']} - {acao['Empresa']}",
                value=f"R$ {acao['Preço']:.2f}",
                delta=f"{acao['Variação (%)']}%"
            )
    else:
        st.warning('Não há dados disponíveis.')



# Adicionar footer padronizado
add_footer()
