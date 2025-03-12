import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from style.style_config import apply_custom_style, COLORS, add_footer
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Aplicar estilo customizado
apply_custom_style()


# Função para calcular a variação percentual
def calcular_variacao(serie, tipo="mensal"):
    # Removendo valores NaN
    valores = serie.dropna()
    if len(valores) < 2:
        return None, None

    valor_atual = valores.iloc[-1]

    if tipo == "diario":
        # Para indicadores diários, compara com o dia anterior
        valor_anterior = valores.iloc[-2]
    elif tipo == "mensal":
        # Convertendo o índice para datetime se não estiver
        if not isinstance(valores.index, pd.DatetimeIndex):
            valores.index = pd.to_datetime(valores.index)
        # Agrupando por mês e pegando o último valor de cada mês
        valores_mensais = valores.groupby(pd.Grouper(freq="ME")).last().dropna()
        if len(valores_mensais) >= 2:
            valor_atual = valores_mensais.iloc[-1]
            valor_anterior = valores_mensais.iloc[-2]
        else:
            return valor_atual, None
    elif tipo == "anual":
        # Para indicadores anuais, compara com o mesmo mês do ano anterior
        if not isinstance(valores.index, pd.DatetimeIndex):
            valores.index = pd.to_datetime(valores.index)
        # Agrupando por ano e pegando o último valor de cada ano
        valores_anuais = valores.groupby(pd.Grouper(freq="Y")).last().dropna()
        if len(valores_anuais) >= 2:
            valor_atual = valores_anuais.iloc[-1]
            valor_anterior = valores_anuais.iloc[-2]
        else:
            return valor_atual, None

    if valor_anterior != 0:
        variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
        return valor_atual, variacao
    return valor_atual, None


# Função para formatar o valor de acordo com o tipo do indicador
def formatar_valor(valor, tipo):
    if valor is None:
        return "N/A"
    if tipo == "moeda":
        return f"R$ {valor:,.2f}"
    elif tipo == "percentual":
        return f"{valor:.2f}%"
    else:
        return f"{valor:.2f}"


# Carregando os dados
@st.cache_data
def carregar_dados():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dados_path = os.path.join(base_path, "results", "dados_economicos.csv")

    # Carregar dados
    df = pd.read_csv(dados_path, parse_dates=["Date"])

    # Criar DataFrames individuais para cada indicador
    selic_df = df[["Date", "SELIC"]].copy()
    selic_df = selic_df.dropna().reset_index(drop=True)
    selic_df["SELIC"] = pd.to_numeric(selic_df["SELIC"], errors="coerce")

    ipca_df = df[["Date", "IPCA"]].copy()
    ipca_df = ipca_df.dropna().reset_index(drop=True)
    ipca_df["IPCA"] = pd.to_numeric(ipca_df["IPCA"], errors="coerce")

    igpm_df = df[["Date", "IGP-M"]].copy()
    igpm_df = igpm_df.dropna().reset_index(drop=True)
    igpm_df["IGP-M"] = pd.to_numeric(igpm_df["IGP-M"], errors="coerce")

    inpc_df = df[["Date", "INPC"]].copy()
    inpc_df = inpc_df.dropna().reset_index(drop=True)
    inpc_df["INPC"] = pd.to_numeric(inpc_df["INPC"], errors="coerce")

    cdi_df = df[["Date", "CDI"]].copy()
    cdi_df = cdi_df.dropna().reset_index(drop=True)
    cdi_df["CDI"] = pd.to_numeric(cdi_df["CDI"], errors="coerce")

    pib_df = df[["Date", "PIB_MENSAL"]].copy()
    pib_df = pib_df.dropna().reset_index(drop=True)
    pib_df["PIB_MENSAL"] = pd.to_numeric(pib_df["PIB_MENSAL"], errors="coerce")

    # Criar dicionário com todos os dataframes
    dataframes = {
        "SELIC": selic_df,
        "IPCA": ipca_df,
        "IGP-M": igpm_df,
        "INPC": inpc_df,
        "CDI": cdi_df,
        "PIB_MENSAL": pib_df,
    }

    return dataframes


# Função para criar features temporais
def criar_features_temporais(df):
    df = df.copy()
    df["ano"] = df["Date"].dt.year
    df["mes"] = df["Date"].dt.month
    df["dia"] = df["Date"].dt.day
    df["dia_semana"] = df["Date"].dt.dayofweek
    df["trimestre"] = df["Date"].dt.quarter
    return df


# Função para treinar modelo de regressão linear
def treinar_regressao_linear(df, indicador, periodos_previsao=6):
    # Verificando se temos dados suficientes, minimo de 2 anos de dados
    if len(df) < 24:
        return None, None, None, None

    # Criar features temporais
    df_features = criar_features_temporais(df)

    # Preparar X e y
    X = df_features[["ano", "mes", "dia", "trimestre"]]
    y = df_features[indicador]

    # Verificar se há valores ausentes ou infinitos
    if np.isinf(y).any() or y.isna().any():
        return None, None, None, None

    # Dividir em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # Normalizar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Treinar modelo
    modelo = LinearRegression()
    modelo.fit(X_train_scaled, y_train)

    # Avaliar modelo
    y_pred = modelo.predict(X_test_scaled)
    mape = mean_absolute_percentage_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    return modelo, scaler, mape, rmse


# Função para fazer previsões
def fazer_previsoes_linear(modelo, scaler, df, indicador, periodos=6):
    # Obter a última data
    ultima_data = df["Date"].iloc[-1]

    # Criar datas futuras
    datas_futuras = pd.date_range(start=ultima_data, periods=periodos + 1, freq="ME")[
        1:
    ]

    # Criar dataframe para previsão
    df_futuro = pd.DataFrame({"Date": datas_futuras})
    df_futuro = criar_features_temporais(df_futuro)

    # Preparar features
    X_futuro = df_futuro[["ano", "mes", "dia", "trimestre"]]
    X_futuro_scaled = scaler.transform(X_futuro)

    # Fazer previsões
    previsoes = modelo.predict(X_futuro_scaled)

    # Calcular intervalo de confiança (usando desvio padrão histórico)
    std_historico = df[indicador].std()
    intervalo_inferior = previsoes - 1.96 * std_historico
    intervalo_superior = previsoes + 1.96 * std_historico

    return (
        pd.Series(previsoes, index=datas_futuras),
        pd.Series(intervalo_inferior, index=datas_futuras),
        pd.Series(intervalo_superior, index=datas_futuras),
    )


# Carregando os dados
df_dict = carregar_dados()

# Título da página
st.title("Indicadores Econômicos do Brasil")
st.markdown("---")

st.markdown("""
    ### Descrição dos Indicadores Econômicos:
    
    - **SELIC**: Taxa básica de juros da economia brasileira, definida pelo Banco Central. É um dos principais instrumentos de política monetária para controle da inflação.
    
    - **IPCA**: Índice de Preços ao Consumidor Amplo, considerado o índice oficial de inflação do Brasil. Mede a variação de preços de produtos e serviços consumidos pelas famílias.
    
    - **IGP-M**: Índice Geral de Preços do Mercado, calculado pela FGV. Muito utilizado para reajustes de contratos de aluguel e tarifas públicas.
    
    - **INPC**: Índice Nacional de Preços ao Consumidor, que mede a variação do custo de vida para famílias com renda de 1 a 5 salários mínimos.
    
    - **CDI**: Certificado de Depósito Interbancário, taxa que serve de referência para investimentos de renda fixa e empréstimos entre bancos.
    
    - **PIB Mensal**: Produto Interno Bruto, representa a soma de todos os bens e serviços produzidos no país, sendo um indicador da atividade econômica.
    """)

st.markdown("---")

# Adicionando CSS para melhorar o layout dos cards
st.markdown(
    """
<style>
    div[data-testid="column"] {
        padding: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Criando cards para cada indicador
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

# Dicionário com informações dos indicadores
indicadores = {
    "SELIC": {
        "nome": "Taxa SELIC",
        "descricao": "Taxa básica de juros da economia",
        "frequencia": "Atualização diária",
        "tipo_valor": "percentual",
        "tipo_variacao": "diario",
        "col": col1,
    },
    "IPCA": {
        "nome": "IPCA",
        "descricao": "Índice de Preços ao Consumidor Amplo",
        "frequencia": "Atualização mensal",
        "tipo_valor": "percentual",
        "tipo_variacao": "mensal",
        "col": col2,
    },
    "IGP-M": {
        "nome": "IGP-M",
        "descricao": "Índice Geral de Preços do Mercado",
        "frequencia": "Atualização mensal",
        "tipo_valor": "percentual",
        "tipo_variacao": "mensal",
        "col": col3,
    },
    "INPC": {
        "nome": "INPC",
        "descricao": "Índice Nacional de Preços ao Consumidor",
        "frequencia": "Atualização mensal",
        "tipo_valor": "percentual",
        "tipo_variacao": "mensal",
        "col": col4,
    },
    "CDI": {
        "nome": "Taxa CDI",
        "descricao": "Certificado de Depósito Interbancário",
        "frequencia": "Atualização diária",
        "tipo_valor": "percentual",
        "tipo_variacao": "diario",
        "col": col5,
    },
    "PIB_MENSAL": {
        "nome": "PIB Mensal",
        "descricao": "Produto Interno Bruto (em milhões R$)",
        "frequencia": "Atualização mensal",
        "tipo_valor": "moeda",
        "tipo_variacao": "mensal",
        "col": col6,
    },
}

# Criando cards e gráficos para cada indicador
for codigo, info in indicadores.items():
    with info["col"]:
        df_indicador = df_dict[codigo]
        serie = df_indicador.set_index("Date")[codigo]
        valor_atual, variacao = calcular_variacao(serie, info["tipo_variacao"])

        # Definindo cores com base na variação
        if variacao is not None:
            if variacao > 0:
                cor_valor = "#00ff00"  # Verde
            elif variacao < 0:
                cor_valor = "#ff0000"  # Vermelho
            else:
                cor_valor = "white"
        else:
            cor_valor = "white"

        # Formatando o valor de acordo com o tipo
        valor_formatado = formatar_valor(valor_atual, info["tipo_valor"])

        st.markdown(
            f"""
            <div style="padding: 20px; border-radius: 10px; background-color: #1a1a1a; color: white; margin: 10px; height: 100%;">
                <h3 style="margin-top: 0;">{info["nome"]}</h3>
                <p style="margin: 10px 0;">{info["descricao"]}</p>
                <p style="color: #888888; font-size: 0.8em; margin: 10px 0;">{info["frequencia"]}</p>
                <h2 style="color: {cor_valor}; margin: 15px 0;">{valor_formatado}</h2>
                <p style="color: {cor_valor}; margin-bottom: 0;">Variação: {"%.2f" % variacao if variacao is not None else "N/A"}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Adicionando espaço entre os cards
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Gráficos
st.markdown("## Evolução dos Indicadores")

tabs = st.tabs([f"**{indicador}**" for indicador in indicadores.keys()])

for (codigo, info), tab in zip(indicadores.items(), tabs):
    with tab:
        df_indicador = df_dict[codigo]

        fig = go.Figure()

        # Linha principal
        fig.add_trace(
            go.Scatter(
                x=df_indicador["Date"],
                y=df_indicador[codigo],
                mode="lines",
                name=info["nome"],
                line=dict(color=COLORS["primary"]),
            )
        )

        # Média móvel 30 dias
        if len(df_indicador) > 30:
            fig.add_trace(
                go.Scatter(
                    x=df_indicador["Date"],
                    y=df_indicador[codigo].rolling(30).mean(),
                    mode="lines",
                    name="Média Móvel (30 dias)",
                    line=dict(color=COLORS["secondary"], dash="dot"),
                )
            )

        fig.update_layout(
            title=f"Evolução do {info['nome']}",
            xaxis_title="Data",
            yaxis_title="Valor",
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

# Tabs para diferentes visualizações
tab1, tab2 = st.tabs(["Comparativo", "Previsões"])

with tab1:
    # Gráfico comparativo (normalizado)
    fig_comp = go.Figure()

    # Lista de cores para o gráfico comparativo
    cores = ["primary", "secondary", "accent", "dark_blue", "text", "background"]

    for i, (codigo, info) in enumerate(indicadores.items()):
        df_indicador = df_dict[codigo]

        # Preparando os dados de acordo com a frequência
        if info["tipo_variacao"] == "mensal":
            # Convertendo para datetime
            df_indicador["Date"] = pd.to_datetime(df_indicador["Date"])
            # Agrupando por mês e pegando o último valor de cada mês
            dados_agrupados = (
                df_indicador.set_index("Date")
                .groupby(pd.Grouper(freq="ME"))
                .last()
                .reset_index()
            )
            dados_agrupados = dados_agrupados.dropna()
        elif info["tipo_variacao"] == "anual":
            # Convertendo para datetime
            df_indicador["Date"] = pd.to_datetime(df_indicador["Date"])
            # Agrupando por ano e pegando o último valor de cada ano
            dados_agrupados = (
                df_indicador.set_index("Date")
                .groupby(pd.Grouper(freq="Y"))
                .last()
                .reset_index()
            )
            dados_agrupados = dados_agrupados.dropna()
        else:
            dados_agrupados = df_indicador

        # Normalizando os dados para comparação
        if len(dados_agrupados) > 0:
            dados_norm = dados_agrupados[codigo] / dados_agrupados[codigo].iloc[0] * 100

            fig_comp.add_trace(
                go.Scatter(
                    x=dados_agrupados["Date"],
                    y=dados_norm,
                    name=info["nome"],
                    line=dict(width=2, color=COLORS[cores[i % len(cores)]]),
                )
            )

    fig_comp.update_layout(
        title="Comparativo da Evolução dos Indicadores (Base 100)",
        xaxis_title="Data",
        yaxis_title="Valor (Base 100)",
        height=600,
        showlegend=True,
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig_comp, use_container_width=True)

with tab2:
    st.markdown("## Previsões dos Indicadores")

    # Seletor de horizonte de previsão
    horizonte = st.slider(
        "Horizonte de Previsão (meses)",
        min_value=1,
        max_value=12,
        value=6,
        help="Selecione quantos meses à frente você deseja prever",
    )

    for codigo, info in indicadores.items():
        st.markdown(f"### {info['nome']}")

        # Preparando os dados
        df_indicador = df_dict[codigo].copy()

        # Verificando se temos dados suficientes
        if len(df_indicador) < 24:
            st.warning(
                f"Dados insuficientes para gerar previsões confiáveis para {info['nome']}"
            )
            continue

        # Tratamento para frequência mensal
        if info["tipo_variacao"] == "mensal":
            # Convertendo para datetime
            df_indicador["Date"] = pd.to_datetime(df_indicador["Date"])
            # Agrupando por mês e pegando o último valor de cada mês
            df_indicador = (
                df_indicador.set_index("Date")
                .groupby(pd.Grouper(freq="ME"))
                .last()
                .reset_index()
            )
            df_indicador = df_indicador.dropna()

        # Treinando modelo de regressão linear
        modelo, scaler, mape, rmse = treinar_regressao_linear(
            df_indicador, codigo, periodos_previsao=horizonte
        )

        if modelo and scaler:
            # Fazendo previsões
            previsoes, intervalo_inf, intervalo_sup = fazer_previsoes_linear(
                modelo, scaler, df_indicador, codigo, periodos=horizonte
            )

            # Plotando resultados
            fig = go.Figure()

            # Dados históricos
            fig.add_trace(
                go.Scatter(
                    x=df_indicador["Date"],
                    y=df_indicador[codigo],
                    name="Dados Históricos",
                    line=dict(color=COLORS["primary"]),
                )
            )

            # Último valor histórico
            ultimo_valor = df_indicador[codigo].iloc[-1]
            fig.add_trace(
                go.Scatter(
                    x=[df_indicador["Date"].iloc[-1]],
                    y=[ultimo_valor],
                    mode="markers",
                    marker=dict(color=COLORS["primary"], size=10),
                    name="Último Valor Real",
                    showlegend=False,
                )
            )

            # Previsões
            fig.add_trace(
                go.Scatter(
                    x=previsoes.index,
                    y=previsoes,
                    name="Previsão",
                    line=dict(color=COLORS["secondary"], dash="dash"),
                )
            )

            # Primeiro valor previsto
            fig.add_trace(
                go.Scatter(
                    x=[previsoes.index[0]],
                    y=[previsoes.iloc[0]],
                    mode="markers",
                    marker=dict(color=COLORS["secondary"], size=10),
                    name="Início da Previsão",
                    showlegend=False,
                )
            )

            # Intervalo de confiança
            fig.add_trace(
                go.Scatter(
                    x=pd.concat(
                        [pd.Series(previsoes.index), pd.Series(previsoes.index[::-1])]
                    ),
                    y=pd.concat([intervalo_sup, intervalo_inf[::-1]]),
                    fill="toself",
                    fillcolor="rgba(0,150,200,0.2)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name="Intervalo de Confiança",
                )
            )

            fig.update_layout(
                title=f"Previsão {info['nome']} - Próximos {horizonte} meses",
                xaxis_title="Data",
                yaxis_title=f"Valor {' (%)' if info['tipo_valor'] == 'percentual' else ' (R$ milhões)' if info['tipo_valor'] == 'moeda' else ''}",
                height=400,
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )

            st.plotly_chart(fig, use_container_width=True)

# Adicionar footer padronizado
add_footer()
