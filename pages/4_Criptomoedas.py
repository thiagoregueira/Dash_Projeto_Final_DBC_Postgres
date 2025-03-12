import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from etl.criptomoedas import obter_melhores_e_piores_cripto, baixar_historico_cripto, get_usdbrl_rate
from style.style_config import apply_custom_style, COLORS, add_footer

# Aplicar estilo customizado
apply_custom_style()

st.title("Criptomoedas")

# # Verifica se o arquivo histórico existe, se não, baixa os dados
# if not pd.io.common.file_exists('../results/historico_criptomoedas.csv'):
#     st.warning('Baixando histórico das criptomoedas... Isso pode levar alguns minutos.')
#     baixar_historico_cripto()

# Obter caminho absoluto para o arquivo
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
historico_path = os.path.join(base_path, 'results', 'historico_criptomoedas.csv')

# Carregar dados históricos
df_cripto = pd.read_csv(historico_path)

# Variável para armazenar o período selecionado
if 'periodo_analise' not in st.session_state:
    st.session_state.periodo_analise = '1y'

# Carregar lista de criptomoedas únicas
criptos = df_cripto['Simbolo'].unique().tolist()

# Campo de seleção da criptomoeda
cripto_selecionada = st.selectbox('Selecione uma criptomoeda:', criptos)

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

# Filtrar dados da criptomoeda selecionada
dados_cripto = df_cripto[df_cripto['Simbolo'] == cripto_selecionada].copy()
dados_cripto['Data'] = pd.to_datetime(dados_cripto['Data'])
dados_cripto = dados_cripto.sort_values('Data')

# Filtrar por período e criar gráfico
data_atual = pd.to_datetime(dados_cripto['Data'].max())
if st.session_state.periodo_analise == '1d':
    data_inicio = data_atual - timedelta(days=30)
    titulo_periodo = 'Últimos 30 dias'
elif st.session_state.periodo_analise == '1mo':
    data_inicio = data_atual - timedelta(days=30 * 12)  # Último ano por mês
    titulo_periodo = 'Variação Mensal'
else:  # '1y'
    data_inicio = data_atual - timedelta(days=365 * 3)  # Últimos 3 anos
    titulo_periodo = 'Variação Anual'

dados_cripto = dados_cripto[dados_cripto['Data'] >= data_inicio]
dados_cripto = dados_cripto.set_index('Data')

# Plotar gráfico de linha
st.subheader(f'Evolução do Preço - {cripto_selecionada} ({titulo_periodo})')
if not dados_cripto.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dados_cripto.index,
        y=dados_cripto['Preco'],
        mode='lines',
        name='Preço',
        line=dict(color=COLORS['primary'])
    ))
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Preço (USD)',
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
    # Obter taxa de câmbio atual
    taxa_usdbrl = get_usdbrl_rate()
    
    with col1:
        preco_usd = dados_cripto['Preco'].iloc[-1]
        preco_brl = preco_usd * taxa_usdbrl
        
        # Mostrar valor em USD e BRL com o mesmo estilo
        st.metric(
            label="Preço Atual",
            value=f"USD {preco_usd:.2f}",
            delta=f"{dados_cripto['Variacao'].iloc[-1]:.2f}%"
        )
        
        # Mostrar valor em BRL com estilo semelhante ao USD
        st.markdown(f"<div style='font-size: 1.5rem; font-weight: 600; margin-top: -15px;'>BRL {preco_brl:.2f}</div>", unsafe_allow_html=True)
    with col2:
        preco_max_usd = dados_cripto['Preco'].max()
        preco_max_brl = preco_max_usd * taxa_usdbrl
        
        st.metric(
            label="Preço Máximo",
            value=f"USD {preco_max_usd:.2f}"
        )
        
        # Mostrar valor em BRL com estilo semelhante ao USD
        st.markdown(f"<div style='font-size: 1.5rem; font-weight: 600; margin-top: -15px;'>BRL {preco_max_brl:.2f}</div>", unsafe_allow_html=True)
    with col3:
        preco_min_usd = dados_cripto['Preco'].min()
        preco_min_brl = preco_min_usd * taxa_usdbrl
        
        st.metric(
            label="Preço Mínimo",
            value=f"USD {preco_min_usd:.2f}"
        )
        
        # Mostrar valor em BRL com estilo semelhante ao USD
        st.markdown(f"<div style='font-size: 1.5rem; font-weight: 600; margin-top: -15px;'>BRL {preco_min_brl:.2f}</div>", unsafe_allow_html=True)
    
    st.info(f'Período: {dados_cripto.index[0].strftime("%d/%m/%Y")} até {dados_cripto.index[-1].strftime("%d/%m/%Y")}')
else:
    st.warning('Não há dados disponíveis para esta criptomoeda no período selecionado.')

# Obter melhores e piores criptomoedas
melhores, piores = obter_melhores_e_piores_cripto(st.session_state.periodo_analise)

# Exibir cards de melhores e piores desempenhos
col1, col2 = st.columns(2)

with col1:
    st.subheader(f'Top 5 - Melhores Criptomoedas ({titulo_periodo})')
    if not melhores.empty:
        for _, cripto in melhores.iterrows():
            preco_usd = cripto['Preço']
            preco_brl = preco_usd * taxa_usdbrl
            
            st.metric(
                label=f"{cripto['Símbolo']} - {cripto['Nome']}",
                value=f"USD {preco_usd:.2f}",
                delta=f"{cripto['Variação (%)']}%"
            )
            
            # Mostrar valor em BRL com estilo semelhante ao USD
            st.markdown(f"<div style='font-size: 1.5rem; font-weight: 600; margin-top: -15px;'>BRL {preco_brl:.2f}</div>", unsafe_allow_html=True)
    else:
        st.warning('Não há dados disponíveis.')

with col2:
    st.subheader(f'Top 5 - Piores Criptomoedas ({titulo_periodo})')
    if not piores.empty:
        for _, cripto in piores.iterrows():
            preco_usd = cripto['Preço']
            preco_brl = preco_usd * taxa_usdbrl
            
            st.metric(
                label=f"{cripto['Símbolo']} - {cripto['Nome']}",
                value=f"USD {preco_usd:.2f}",
                delta=f"{cripto['Variação (%)']}%"
            )
            
            # Mostrar valor em BRL com estilo semelhante ao USD
            st.markdown(f"<div style='font-size: 1.5rem; font-weight: 600; margin-top: -15px;'>BRL {preco_brl:.2f}</div>", unsafe_allow_html=True)
    else:
        st.warning('Não há dados disponíveis.')

# Adicionar footer padronizado
add_footer()
