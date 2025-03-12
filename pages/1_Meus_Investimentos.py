import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from style.style_config import apply_custom_style, COLORS, add_footer
from auth.user import authenticate_user, get_logged_user, get_user_cpf, get_user_data_by_cpf
# Importar funções do módulo db.db
from db.db import (
    get_usuario_by_cpf_senha,
    get_pessoa_by_id_usuario,
    get_contas_by_id_pessoa,
    get_investimentos_by_id_conta,
    get_fundos_by_id_investimento,
    get_criptos_by_id_investimento,
    get_acoes_by_id_investimento,
    get_all_dataframes
)

# Aplicar estilo customizado
apply_custom_style()

st.title("Meus Investimentos")


# Função para obter os dados do usuário logado
def obter_dados_usuario():
    """Obtém os dados do usuário logado usando o token de autenticação"""
    try:
        # Obter o CPF do usuário logado através do token
        cpf = get_user_cpf()
        if not cpf:
            # Se não conseguir obter o CPF, tenta obter os dados básicos
            user_data = get_logged_user()
            
            if user_data:
                # Extrair informações relevantes
                return {
                    "autenticado": True,
                    "id_usuario": user_data.get("idUsuario"),
                    "id_pessoa": user_data.get("idPessoa"),
                    "nome": user_data.get("nome"),
                    "id_conta": user_data.get("idConta")
                }
            return {"autenticado": False}
        
        # Obter todos os dados do usuário a partir do CPF
        dados_completos = get_user_data_by_cpf(cpf)
        
        if dados_completos:
            dados_usuario = dados_completos["dados_usuario"]
            dados_pessoa = dados_completos["dados_pessoa"]
            contas = dados_completos["contas"]
            
            # Usar o id_conta fornecido pelos dados completos
            id_conta = dados_completos.get("id_conta")
            
            # Se não houver id_conta, usar o da primeira conta se houver contas
            if not id_conta and contas and len(contas) > 0:
                # Verificar se estamos lidando com dados da API ou do banco de dados
                if isinstance(contas[0], dict) and "idConta" in contas[0]:
                    id_conta = contas[0].get("idConta")
                elif isinstance(contas[0], dict) and "id_conta" in contas[0]:
                    id_conta = contas[0].get("id_conta")
            
            # Criar dicionário de retorno com os dados disponíveis
            resultado = {
                "autenticado": True,
                "cpf": cpf,
                "id_conta": id_conta
            }
            
            # Adicionar dados do usuário se disponíveis
            if isinstance(dados_usuario, dict):
                # Verificar se estamos lidando com dados da API ou do banco de dados
                if "idUsuario" in dados_usuario:
                    resultado["id_usuario"] = dados_usuario.get("idUsuario")
                elif "id_usuario" in dados_usuario:
                    resultado["id_usuario"] = dados_usuario.get("id_usuario")
            
            # Adicionar dados da pessoa se disponíveis
            if isinstance(dados_pessoa, dict):
                # Verificar se estamos lidando com dados da API ou do banco de dados
                if "idPessoa" in dados_pessoa:
                    resultado["id_pessoa"] = dados_pessoa.get("idPessoa")
                    resultado["nome"] = dados_pessoa.get("nome")
                    resultado["email"] = dados_pessoa.get("email")
                    resultado["telefone"] = dados_pessoa.get("telefone")
                    resultado["sexo"] = dados_pessoa.get("sexo")
                    resultado["dt_nascimento"] = dados_pessoa.get("dtNascimento")
                elif "id_pessoa" in dados_pessoa:
                    resultado["id_pessoa"] = dados_pessoa.get("id_pessoa")
                    resultado["nome"] = dados_pessoa.get("nome")
                    resultado["email"] = dados_pessoa.get("email")
                    resultado["telefone"] = dados_pessoa.get("telefone")
                    resultado["sexo"] = dados_pessoa.get("sexo")
                    resultado["dt_nascimento"] = dados_pessoa.get("dt_nascimento")
            
            # Adicionar contas
            resultado["contas"] = contas
            
            return resultado
            
        return {"autenticado": False}
    except Exception as e:
        st.error(f"Erro ao obter dados do usuário: {e}")
        return {"autenticado": False}


# Função para obter os investimentos do cliente
def obter_investimentos_cliente(id_conta=None):
    """Obtém os investimentos do cliente usando o token e o CPF.
    
    Args:
        id_conta (int, optional): ID da conta para filtrar investimentos. 
            Se None, tenta buscar todas as contas do usuário.
    """
    # Importar funções para atualização de preços
    from etl.criptomoedas import get_current_prices
    from etl.acoes import get_current_prices_acoes
    
    try:
        # Verificar se há token na sessão
        token = st.session_state.get("token")
        if not token:
            st.error("Usuário não autenticado. Faça login novamente.")
            return None, None, None, None
        
        # Obter o CPF do usuário logado usando a API
        cpf = get_user_cpf()
        if not cpf:
            st.error("Não foi possível obter o CPF do usuário.")
            return None, None, None, None
            
        if st.session_state.get("debug_mode", False):
            st.sidebar.success(f"CPF obtido da API: {cpf}")
        
        # 1. Obter dados do usuário pelo CPF
        df_usuario = get_usuario_by_cpf_senha(cpf, None)
        if df_usuario.empty:
            st.error("Usuário não encontrado no banco de dados.")
            return None, None, None, None
            
        id_usuario = df_usuario.iloc[0]["id_usuario"]
        
        # 2. Obter dados da pessoa pelo ID do usuário
        df_pessoa = get_pessoa_by_id_usuario(id_usuario)
        if df_pessoa.empty:
            st.error("Dados da pessoa não encontrados no banco de dados.")
            return None, None, None, None
            
        id_pessoa = df_pessoa.iloc[0]["id_pessoa"]
        
        # 3. Obter contas pelo ID da pessoa
        df_contas = get_contas_by_id_pessoa(id_pessoa)
        if df_contas.empty:
            st.warning("Usuário não possui contas cadastradas no banco de dados.")
            return None, None, None, None
        
        # Filtrar por id_conta se fornecido
        if id_conta:
            df_contas = df_contas[df_contas["id_conta"] == id_conta]
            if df_contas.empty:
                st.warning(f"Conta com ID {id_conta} não encontrada no banco de dados.")
                return None, None, None, None
        
        # Usar as contas obtidas diretamente do banco de dados
        contas_cliente = df_contas
            
    except Exception as e:
        st.error(f"Erro ao obter investimentos: {e}")
        return None, None, None, None

    # Lista para armazenar todos os investimentos
    investimentos = []

    # Armazenar o perfil do cliente
    perfil_cliente = "CONSERVADOR"

    # Para cada conta do cliente
    for _, conta in contas_cliente.iterrows():
        # Obter os investimentos da conta diretamente do banco de dados
        investimentos_conta = get_investimentos_by_id_conta(conta["id_conta"])

        if investimentos_conta.empty:
            continue

        # Perfil de investimento do cliente para esta conta
        perfil_cliente = investimentos_conta.iloc[0]["perfil_invest"]

        # Para cada investimento vinculado à conta
        for _, inv in investimentos_conta.iterrows():
            id_investimento = inv["id_investimento"]

            # Obter todos os fundos vinculados a este ID de investimento diretamente do banco de dados
            fundos = get_fundos_by_id_investimento(id_investimento)

            # Processar cada fundo individualmente
            for _, fundo in fundos.iterrows():
                # Verificar se o investimento está ativo
                data_enc = fundo.get("data_encerramento", None)
                ativo = True

                if pd.notna(data_enc):
                    data_enc = pd.to_datetime(data_enc)
                    ativo = data_enc > datetime.now()

                if ativo:
                    # Calcular valor atual com juros compostos
                    valor_investido = fundo["valor_investido"]
                    rentabilidade_mensal = fundo["rentabilidade"]
                    data_aplicacao = pd.to_datetime(fundo["data_aplicacao"])

                    # Número de meses desde a aplicação
                    hoje = datetime.now()
                    meses_decorridos = (
                        (hoje.year - data_aplicacao.year) * 12
                        + hoje.month
                        - data_aplicacao.month
                    )

                    # Cálculo de juros compostos
                    valor_atual = (
                        valor_investido * (1 + rentabilidade_mensal) ** meses_decorridos
                    )

                    # Usar id_fundo em vez de id_investimento
                    investimentos.append(
                        {
                            "id": fundo[
                                "id_fundo"
                            ],
                            "nome": fundo["nome"],
                            "tipo": "Fundo",
                            "valor_investido": valor_investido,
                            "valor_atual": valor_atual,
                            "perfil_risco": fundo["perfil_risco"],
                            "rentabilidade": rentabilidade_mensal,
                            "data_aplicacao": fundo["data_aplicacao"],
                        }
                    )

            # Obter todas as criptos vinculadas a este ID de investimento diretamente do banco de dados
            criptos = get_criptos_by_id_investimento(id_investimento)

            # Processar cada cripto individualmente
            for _, cripto in criptos.iterrows():
                # Verificar se o investimento está ativo
                data_enc = cripto.get("data_encerramento", None)
                ativo = True

                if pd.notna(data_enc):
                    data_enc = pd.to_datetime(data_enc)
                    ativo = data_enc > datetime.now()

                if ativo:
                    # Criar um DataFrame temporário com esta criptomoeda para atualizar o preço
                    cripto_temp_df = pd.DataFrame([cripto])
                    
                    # Atualizar preços usando a função get_current_prices
                    atualizado_df = get_current_prices(cripto_temp_df)
                    
                    # Extrair informações do DataFrame atualizado
                    valor_investido = atualizado_df.iloc[0]["valor_investido_br"]
                    preco_compra = atualizado_df.iloc[0]["preco_compra_br"]
                    preco_atual = atualizado_df.iloc[0]["preco_atual_br"]
                    
                    # Calcular valor atual baseado na diferença de preço
                    if preco_compra > 0:
                        valor_atual = (valor_investido / preco_compra) * preco_atual
                    else:
                        valor_atual = valor_investido  # Fallback se preço de compra for zero
                    
                    # Calcular rentabilidade baseada na variação de preço
                    rentabilidade = (preco_atual / preco_compra) - 1 if preco_compra > 0 else 0

                    investimentos.append(
                        {
                            "id": cripto["id_cripto"],
                            "nome": cripto["nome"],
                            "tipo": "Cripto",
                            "valor_investido": valor_investido,
                            "valor_atual": valor_atual,
                            "perfil_risco": cripto["perfil_risco"],
                            "rentabilidade": rentabilidade,
                            "data_aplicacao": cripto["data_aplicacao"],
                        }
                    )

            # Obter todas as ações vinculadas a este ID de investimento diretamente do banco de dados
            acoes = get_acoes_by_id_investimento(id_investimento)

            # Processar cada ação individualmente
            for _, acao in acoes.iterrows():
                # Verificar se o investimento está ativo
                data_enc = acao.get("data_encerramento", None)
                ativo = True

                if pd.notna(data_enc):
                    data_enc = pd.to_datetime(data_enc)
                    ativo = data_enc > datetime.now()

                if ativo:
                    # Criar um DataFrame temporário com esta ação para atualizar o preço
                    acao_temp_df = pd.DataFrame([acao])
                    
                    # Atualizar preços usando a função get_current_prices_acoes
                    atualizado_df = get_current_prices_acoes(acao_temp_df)
                    
                    # Extrair informações do DataFrame atualizado
                    quantidade = atualizado_df.iloc[0]["quantidade"]
                    preco_inicial = atualizado_df.iloc[0]["preco_inicial"]
                    preco_atual = atualizado_df.iloc[0]["preco_atual_br"]
                    
                    # Calcular valor investido e valor atual
                    valor_investido = quantidade * preco_inicial
                    valor_atual = quantidade * preco_atual
                    
                    # Calcular rentabilidade baseada na variação de preço
                    rentabilidade = (preco_atual / preco_inicial) - 1 if preco_inicial > 0 else 0

                    investimentos.append(
                        {
                            "id": acao["id_acoes"],
                            "nome": acao["nome"],
                            "tipo": "Ações",
                            "valor_investido": valor_investido,
                            "valor_atual": valor_atual,
                            "perfil_risco": acao["perfil_risco"],
                            "rentabilidade": rentabilidade,
                            "data_aplicacao": acao["data_aplicacao"],
                        }
                    )

    # Criar DataFrame com os investimentos
    df_investimentos = pd.DataFrame(investimentos)

    if df_investimentos.empty:
        return None, None, perfil_cliente, None

    # Calcular alocação atual por perfil de risco baseado no valor investido
    alocacao_atual_investido = (
        df_investimentos.groupby("perfil_risco")["valor_investido"].sum().reset_index()
    )
    total_investido = alocacao_atual_investido["valor_investido"].sum()
    alocacao_atual_investido["percentual"] = (
        alocacao_atual_investido["valor_investido"] / total_investido
    ) * 100
    
    # Calcular alocação atual por perfil de risco baseado no valor atual
    alocacao_atual = (
        df_investimentos.groupby("perfil_risco")["valor_atual"].sum().reset_index().rename(columns={"valor_atual": "valor_investido"})
    )
    total_atual = alocacao_atual["valor_investido"].sum()
    alocacao_atual["percentual"] = (
        alocacao_atual["valor_investido"] / total_atual
    ) * 100

    return df_investimentos, alocacao_atual, perfil_cliente, alocacao_atual_investido


# Função para calcular a alocação ideal com base no perfil
def calcular_alocacao_ideal(perfil, total_investido):
    if perfil == "CONSERVADOR":
        return pd.DataFrame(
            {
                "perfil_risco": ["BAIXO", "MODERADO", "ALTO"],
                "percentual": [70, 30, 0],
                "valor_investido": [total_investido * 0.7, total_investido * 0.3, 0],
            }
        )
    elif perfil == "MODERADO":
        return pd.DataFrame(
            {
                "perfil_risco": ["BAIXO", "MODERADO", "ALTO"],
                "percentual": [40, 50, 10],
                "valor_investido": [
                    total_investido * 0.4,
                    total_investido * 0.5,
                    total_investido * 0.1,
                ],
            }
        )
    else:  # ARROJADO
        return pd.DataFrame(
            {
                "perfil_risco": ["BAIXO", "MODERADO", "ALTO"],
                "percentual": [20, 30, 50],
                "valor_investido": [
                    total_investido * 0.2,
                    total_investido * 0.3,
                    total_investido * 0.5,
                ],
            }
        )


# Função para criar o gráfico de barras comparativo
def criar_grafico_comparativo(alocacao_atual, alocacao_ideal):
    # Garantir a ordem correta das categorias
    categorias_ordem = ["BAIXO", "MODERADO", "ALTO"]

    # Reorganizar os DataFrames para seguir a ordem desejada
    alocacao_atual = (
        pd.DataFrame(alocacao_atual)
        .set_index("perfil_risco")
        .reindex(categorias_ordem)
        .reset_index()
    )
    alocacao_ideal = (
        pd.DataFrame(alocacao_ideal)
        .set_index("perfil_risco")
        .reindex(categorias_ordem)
        .reset_index()
    )

    fig = go.Figure()

    # Adicionar barras para alocação atual
    fig.add_trace(
        go.Bar(
            x=alocacao_atual["perfil_risco"],
            y=alocacao_atual["percentual"],
            name="Alocação Atual",
            marker_color=COLORS["primary"],
            text=[f"{p:.1f}%" for p in alocacao_atual["percentual"]],
            textposition="auto",
        )
    )

    # Adicionar barras para alocação ideal
    fig.add_trace(
        go.Bar(
            x=alocacao_ideal["perfil_risco"],
            y=alocacao_ideal["percentual"],
            name="Alocação Ideal",
            marker_color=COLORS["secondary"],
            text=[f"{p:.1f}%" for p in alocacao_ideal["percentual"]],
            textposition="auto",
        )
    )

    # Atualizar layout do gráfico
    fig.update_layout(
        title="Comparação entre Alocação Atual e Ideal",
        xaxis_title="Perfil de Risco",
        xaxis={"categoryorder": "array", "categoryarray": categorias_ordem},
        yaxis_title="Percentual (%)",
        template="plotly_dark",
        plot_bgcolor=COLORS["background_graph"],
        paper_bgcolor=COLORS["background"],
        font=dict(color=COLORS["text"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
    )

    return fig


# Função para criar o gráfico de pizza da composição atual
def criar_grafico_pizza(alocacao_atual):
    fig = px.pie(
        alocacao_atual,
        values="valor_investido",
        names="perfil_risco",
        title="Composição Atual da Carteira",
        color="perfil_risco",
        color_discrete_map={
            "BAIXO": "#00BFA5",
            "MODERADO": "#0288D1",
            "ALTO": "#D32F2F",
        },
        hole=0.4,
    )

    # Atualizar layout do gráfico
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=COLORS["background_graph"],
        paper_bgcolor=COLORS["background"],
        font=dict(color=COLORS["text"]),
        height=400,
    )

    return fig


# Função para criar o gráfico de pizza da composição ideal
def criar_grafico_pizza_ideal(alocacao_ideal):
    fig = px.pie(
        alocacao_ideal,
        values="valor_investido",
        names="perfil_risco",
        title="Composição Ideal para seu Perfil",
        color="perfil_risco",
        color_discrete_map={
            "BAIXO": "#00BFA5",
            "MODERADO": "#0288D1",
            "ALTO": "#D32F2F",
        },
        hole=0.4,
    )

    # Atualizar layout do gráfico
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=COLORS["background_graph"],
        paper_bgcolor=COLORS["background"],
        font=dict(color=COLORS["text"]),
        height=400,
    )

    return fig


# Interface de usuário
if "token" not in st.session_state:
    st.session_state.usuario_autenticado = False
    st.session_state.dados_usuario = None
else:
    # Se já temos um token, verificar se ainda é válido obtendo os dados do usuário
    dados_usuario = obter_dados_usuario()
    if dados_usuario["autenticado"]:
        st.session_state.usuario_autenticado = True
        st.session_state.dados_usuario = dados_usuario
        
        # # Exibir informações de debug (remover em produção)
        # if st.session_state.get("debug_mode", False):
        #     st.sidebar.write("Dados do usuário:", dados_usuario)
    else:
        # Token inválido ou expirado
        st.session_state.usuario_autenticado = False
        st.session_state.dados_usuario = None
        if "token" in st.session_state:
            del st.session_state.token

# Área de autenticação
if not st.session_state.usuario_autenticado:
    with st.form("login_form"):
        st.subheader("Acesse sua conta FinUP Investimentos")
        cpf = st.text_input("CPF (apenas números)", max_chars=11)
        senha = st.text_input("Senha", type="password")

        # Botão de login
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if cpf and senha:
                # Autenticar usando a função do módulo auth.user
                token = authenticate_user(cpf, senha)

                if token:
                    # Obter dados do usuário usando o token
                    dados_usuario = obter_dados_usuario()
                    
                    if dados_usuario["autenticado"]:
                        st.session_state.usuario_autenticado = True
                        st.session_state.dados_usuario = dados_usuario
                        st.success(f"Bem-vindo(a), {dados_usuario['nome']}!")
                        st.rerun()
                    else:
                        st.error("Erro ao obter dados do usuário. Tente novamente.")
                else:
                    st.error("CPF ou senha inválidos. Tente novamente.")
            else:
                st.warning("Por favor, preencha todos os campos.")
else:
    # Exibir dados do usuário logado
    st.sidebar.success(f"Cliente FinUP: {st.session_state.dados_usuario['nome']}")

    # Botão para logout
    if st.sidebar.button("Sair"):
        st.session_state.usuario_autenticado = False
        st.session_state.dados_usuario = None
        if "token" in st.session_state:
            del st.session_state.token
        st.rerun()
    
    # Botão para ativar/desativar modo de depuração (apenas para desenvolvimento)
    # with st.sidebar.expander("Opções avançadas"):
    #     if st.checkbox("Modo de depuração", value=st.session_state.get("debug_mode", False)):
    #         st.session_state.debug_mode = True
    #         st.info("Modo de depuração ativado. Informações detalhadas serão exibidas.")
            
    #         # Exibir informações do usuário
    #         st.write("**Dados do usuário:**")
    #         st.json(st.session_state.dados_usuario)
            
    #         # Exibir CPF do usuário
    #         cpf = get_user_cpf()
    #         st.write(f"**CPF do usuário:** {cpf if cpf else 'Não disponível'}")
    #     else:
    #         st.session_state.debug_mode = False

    # # Botão para recarregar os dados
    # if st.sidebar.button("🔄 Atualizar Dados"):
    #     st.cache_data.clear()
    #     st.rerun()

    # Obter investimentos do cliente usando o ID da conta
    df_investimentos, alocacao_atual, perfil_cliente, alocacao_atual_investido = obter_investimentos_cliente(
        st.session_state.dados_usuario["id_conta"]
    )
    
    # Exibir informações de debug
    if st.session_state.get("debug_mode", False):
        st.sidebar.info(f"Buscando investimentos para a conta ID: {st.session_state.dados_usuario['id_conta']}")

    if df_investimentos is None:
        st.warning("Você não possui investimentos ativos.")
    else:
        # Mostrar o perfil de investimento do cliente
        st.info(f"Seu perfil de investimento: **{perfil_cliente}**")

        # Calcular total investido usando os mesmos valores da aba de detalhes
        # Vamos primeiro obter os dados para as tabelas da aba detalhes
        # Fundos
        df_fundos_tab = df_investimentos[df_investimentos["tipo"] == "Fundo"].copy()
        
        # Criptomoedas
        _, _, _, _, _, df_cripto_original, df_acoes_original = get_all_dataframes()
        ids_cripto = df_investimentos[df_investimentos["tipo"] == "Cripto"]["id"].tolist()
        df_cripto_tab = df_cripto_original[df_cripto_original["id_cripto"].isin(ids_cripto)].copy()
        from etl.criptomoedas import get_current_prices
        cripto_df_tab = get_current_prices(df_cripto_tab.copy(deep=True))
        
        # Ações
        ids_acoes = df_investimentos[df_investimentos["tipo"] == "Ações"]["id"].tolist()
        df_acoes_tab = df_acoes_original[df_acoes_original["id_acoes"].isin(ids_acoes)].copy()
        from etl.acoes import get_current_prices_acoes
        acoes_df_tab = get_current_prices_acoes(df_acoes_tab.copy(deep=True))
        
        # Agora somamos os valores investidos de cada tipo de investimento
        total_fundos = df_fundos_tab["valor_investido"].sum()
        total_criptos = cripto_df_tab["valor_investido_br"].sum()
        total_acoes = acoes_df_tab["valor_investido_br"].sum()
        
        # Total investido é a soma de todos os tipos de investimento
        total_investido = total_fundos + total_criptos + total_acoes

        # Calcular total acumulado (soma de todos os valores atuais)
        total_acumulado = df_investimentos["valor_atual"].sum()

        # Calcular a rentabilidade total
        rentabilidade_total = ((total_acumulado / total_investido) - 1) * 100

        # Criar duas colunas para exibir os totais lado a lado
        col1, col2 = st.columns(2)

        # Exibir total investido na primeira coluna
        with col1:
            st.metric(
                "Total Investido",
                f"R$ {total_investido:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
            )

        # Exibir total acumulado na segunda coluna, com indicador delta mostrando a rentabilidade
        with col2:
            st.metric(
                "Total Acumulado",
                f"R$ {total_acumulado:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta=f"{rentabilidade_total:.2f}%",
                delta_color="normal",
            )

        # Calcular alocação ideal baseada no total investido original
        # Mantemos isso para compatibilidade com outras partes do código
        alocacao_ideal = calcular_alocacao_ideal(perfil_cliente, total_investido)

        # Criar abas para os diferentes gráficos e tabelas
        tab1, tab2, tab3 = st.tabs(["Comparativo", "Composição", "Detalhes"])

        with tab1:
            # Calcular alocação atual baseada nos valores atuais - agrupar por perfil_risco
            # O valor será a soma de valor_atual (mais atualizado)
            alocacao_atual_corrigida = (
                df_investimentos.groupby("perfil_risco")["valor_atual"]
                .sum()
                .reset_index()
                .rename(columns={"valor_atual": "valor_investido"})
            )
            total_atual_corrigido = alocacao_atual_corrigida[
                "valor_investido"
            ].sum()
            alocacao_atual_corrigida["percentual"] = (
                alocacao_atual_corrigida["valor_investido"] / total_atual_corrigido
            ) * 100

            # Gráfico de barras comparativo
            fig_comparativo = criar_grafico_comparativo(
                alocacao_atual_corrigida, alocacao_ideal
            )
            st.plotly_chart(fig_comparativo, use_container_width=True)

            # Preparar os dados para análise e recomendações
            # Calculando o total investido para usar na alocação ideal
            total_investido_original = df_investimentos["valor_investido"].sum()
            
            # Recalcular alocação ideal com base no total investido original
            alocacao_ideal_recalculada = calcular_alocacao_ideal(perfil_cliente, total_investido_original)
            
            # Agora comparamos a alocação atual (baseada nos valores atuais) com a ideal
            alocacao_dict = {
                row["perfil_risco"]: {
                    "atual_perc": row["percentual"],
                    "atual_valor": row["valor_investido"],  # Este já é o valor atual
                    "ideal_perc": alocacao_ideal_recalculada[
                        alocacao_ideal_recalculada["perfil_risco"] == row["perfil_risco"]
                    ]["percentual"].values[0]
                    if row["perfil_risco"] in alocacao_ideal_recalculada["perfil_risco"].values
                    else 0,
                    "ideal_valor": alocacao_ideal_recalculada[
                        alocacao_ideal_recalculada["perfil_risco"] == row["perfil_risco"]
                    ]["valor_investido"].values[0]
                    if row["perfil_risco"] in alocacao_ideal_recalculada["perfil_risco"].values
                    else 0,
                }
                for _, row in alocacao_atual_corrigida.iterrows()
            }

            # Adicionar perfis que existem no ideal mas não no atual
            for _, row in alocacao_ideal_recalculada.iterrows():
                if row["perfil_risco"] not in alocacao_dict:
                    alocacao_dict[row["perfil_risco"]] = {
                        "atual_perc": 0,
                        "atual_valor": 0,
                        "ideal_perc": row["percentual"],
                        "ideal_valor": row["valor_investido"],
                    }

            # Verificar se a carteira está fora do perfil recomendado, com tolerancia de 5%
            perfis_desbalanceados = []
            for perfil, dados in alocacao_dict.items():
                if (
                    abs(dados["atual_perc"] - dados["ideal_perc"]) > 5
                ):
                    perfis_desbalanceados.append((perfil, dados))

            if perfis_desbalanceados:
                st.warning(
                    "⚠️ Sua carteira está desbalanceada em relação ao seu perfil:"
                )

                # Ordenar os perfis na ordem: Baixo, Moderado, Alto
                ordem_perfis = {"Baixo": 0, "Moderado": 1, "Alto": 2}
                perfis_desbalanceados.sort(key=lambda x: ordem_perfis.get(x[0], 999))

                # Lógica geral
                recomendacoes = []

                # Para perfil Conservador - tratar primeiro o Alto Risco, zerando
                if perfil_cliente == "Conservador":
                    # Verificar se tem investimentos em Alto
                    if (
                        "Alto" in alocacao_dict
                        and alocacao_dict["Alto"]["atual_valor"] > 0
                    ):
                        valor_alto = alocacao_dict["Alto"]["atual_valor"]
                        # Verificar se pode mover para Moderado
                        espaco_moderado = (
                            (
                                alocacao_dict["Moderado"]["ideal_valor"]
                                - alocacao_dict["Moderado"]["atual_valor"]
                            )
                            if "Moderado" in alocacao_dict
                            else 0
                        )

                        if espaco_moderado > 0:
                            valor_para_moderado = min(valor_alto, espaco_moderado)
                            valor_para_baixo = valor_alto - valor_para_moderado

                            if valor_para_moderado > 0:
                                recomendacoes.append(
                                    f"- **Realocação Alto → Moderado**: Transfira **R$ {valor_para_moderado:,.2f}** dos investimentos de risco **Alto** para **Moderado**".replace(
                                        ",", "X"
                                    )
                                    .replace(".", ",")
                                    .replace("X", ".")
                                )

                            if valor_para_baixo > 0:
                                recomendacoes.append(
                                    f"- **Realocação Alto → Baixo**: Transfira **R$ {valor_para_baixo:,.2f}** dos investimentos de risco **Alto** para **Baixo**".replace(
                                        ",", "X"
                                    )
                                    .replace(".", ",")
                                    .replace("X", ".")
                                )
                        else:
                            # Mover tudo para Baixo
                            recomendacoes.append(
                                f"- **Realocação Alto → Baixo**: Transfira **R$ {valor_alto:,.2f}** dos investimentos de risco **Alto** para **Baixo**".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", ".")
                            )

                    # Verificar se Moderado está acima do ideal
                    if (
                        "Moderado" in alocacao_dict
                        and alocacao_dict["Moderado"]["atual_valor"]
                        > alocacao_dict["Moderado"]["ideal_valor"]
                    ):
                        excesso_moderado = (
                            alocacao_dict["Moderado"]["atual_valor"]
                            - alocacao_dict["Moderado"]["ideal_valor"]
                        )
                        recomendacoes.append(
                            f"- **Realocação Moderado → Baixo**: Transfira **R$ {excesso_moderado:,.2f}** dos investimentos de risco **Moderado** para **Baixo**".replace(
                                ",", "X"
                            )
                            .replace(".", ",")
                            .replace("X", ".")
                        )

                    # Verificar se Baixo precisa de mais investimento
                    if (
                        "Baixo" in alocacao_dict
                        and alocacao_dict["Baixo"]["atual_valor"]
                        < alocacao_dict["Baixo"]["ideal_valor"]
                    ):
                        falta_baixo = (
                            alocacao_dict["Baixo"]["ideal_valor"]
                            - alocacao_dict["Baixo"]["atual_valor"]
                        )
                        # Se ainda faltam investimentos após realocações
                        falta_apos_realocacoes = True
                        for rec in recomendacoes:
                            if "→ Baixo" in rec:
                                falta_apos_realocacoes = False

                        if falta_apos_realocacoes:
                            recomendacoes.append(
                                f"- **Aumentar Baixo**: Invista mais **R$ {falta_baixo:,.2f}** em ativos de risco **Baixo**".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", ".")
                            )

                # Para perfil Moderado
                elif perfil_cliente == "Moderado":
                    # Verificar se Alto está acima do ideal
                    if (
                        "Alto" in alocacao_dict
                        and alocacao_dict["Alto"]["atual_valor"]
                        > alocacao_dict["Alto"]["ideal_valor"]
                    ):
                        excesso_alto = (
                            alocacao_dict["Alto"]["atual_valor"]
                            - alocacao_dict["Alto"]["ideal_valor"]
                        )
                        # Verificar espaço em Moderado e Baixo
                        espaco_moderado = (
                            (
                                alocacao_dict["Moderado"]["ideal_valor"]
                                - alocacao_dict["Moderado"]["atual_valor"]
                            )
                            if "Moderado" in alocacao_dict
                            else 0
                        )

                        if espaco_moderado > 0:
                            valor_para_moderado = min(excesso_alto, espaco_moderado)
                            valor_para_baixo = excesso_alto - valor_para_moderado

                            if valor_para_moderado > 0:
                                recomendacoes.append(
                                    f"- **Realocação Alto → Moderado**: Transfira **R$ {valor_para_moderado:,.2f}** dos investimentos de risco **Alto** para **Moderado**".replace(
                                        ",", "X"
                                    )
                                    .replace(".", ",")
                                    .replace("X", ".")
                                )

                            if valor_para_baixo > 0:
                                recomendacoes.append(
                                    f"- **Realocação Alto → Baixo**: Transfira **R$ {valor_para_baixo:,.2f}** dos investimentos de risco **Alto** para **Baixo**".replace(
                                        ",", "X"
                                    )
                                    .replace(".", ",")
                                    .replace("X", ".")
                                )
                        else:
                            # Mover tudo para Baixo
                            recomendacoes.append(
                                f"- **Realocação Alto → Baixo**: Transfira **R$ {excesso_alto:,.2f}** dos investimentos de risco **Alto** para **Baixo**".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", ".")
                            )

                    # Verificar se Moderado está acima do ideal
                    if (
                        "Moderado" in alocacao_dict
                        and alocacao_dict["Moderado"]["atual_valor"]
                        > alocacao_dict["Moderado"]["ideal_valor"]
                    ):
                        excesso_moderado = (
                            alocacao_dict["Moderado"]["atual_valor"]
                            - alocacao_dict["Moderado"]["ideal_valor"]
                        )
                        recomendacoes.append(
                            f"- **Realocação Moderado → Baixo**: Transfira **R$ {excesso_moderado:,.2f}** dos investimentos de risco **Moderado** para **Baixo**".replace(
                                ",", "X"
                            )
                            .replace(".", ",")
                            .replace("X", ".")
                        )

                    # Verificar se Alto precisa de mais investimento
                    if (
                        "Alto" in alocacao_dict
                        and alocacao_dict["Alto"]["atual_valor"]
                        < alocacao_dict["Alto"]["ideal_valor"]
                    ):
                        falta_alto = (
                            alocacao_dict["Alto"]["ideal_valor"]
                            - alocacao_dict["Alto"]["atual_valor"]
                        )
                        recomendacoes.append(
                            f"- **Aumentar Alto**: Invista mais **R$ {falta_alto:,.2f}** em ativos de risco **Alto**".replace(
                                ",", "X"
                            )
                            .replace(".", ",")
                            .replace("X", ".")
                        )

                    # Verificar se Moderado precisa de mais investimento
                    if (
                        "Moderado" in alocacao_dict
                        and alocacao_dict["Moderado"]["atual_valor"]
                        < alocacao_dict["Moderado"]["ideal_valor"]
                    ):
                        falta_moderado = (
                            alocacao_dict["Moderado"]["ideal_valor"]
                            - alocacao_dict["Moderado"]["atual_valor"]
                        )
                        
                        # Verificar se já existe recomendação de transferência para Moderado
                        transferencia_para_moderado = False
                        for rec in recomendacoes:
                            if "→ Moderado" in rec:
                                transferencia_para_moderado = True
                                break
                                
                        # Só adicionar recomendação se não houver transferência para Moderado
                        if not transferencia_para_moderado:
                            recomendacoes.append(
                                f"- **Aumentar Moderado**: Invista mais **R$ {falta_moderado:,.2f}** em ativos de risco **Moderado**".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", ".")
                            )

                # Para perfil Arrojado
                else:  # perfil_cliente == "Arrojado"
                    # Verificar se Baixo e Moderado estão acima do ideal
                    if (
                        "Baixo" in alocacao_dict
                        and alocacao_dict["Baixo"]["atual_valor"]
                        > alocacao_dict["Baixo"]["ideal_valor"]
                    ):
                        excesso_baixo = (
                            alocacao_dict["Baixo"]["atual_valor"]
                            - alocacao_dict["Baixo"]["ideal_valor"]
                        )
                        # Verificar qual categoria precisa de mais investimento
                        if (
                            "Alto" in alocacao_dict
                            and alocacao_dict["Alto"]["atual_valor"]
                            < alocacao_dict["Alto"]["ideal_valor"]
                        ):
                            recomendacoes.append(
                                f"- **Realocação Baixo → Alto**: Transfira **R$ {excesso_baixo:,.2f}** dos investimentos de risco **Baixo** para **Alto**".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", ".")
                            )
                        elif (
                            "Moderado" in alocacao_dict
                            and alocacao_dict["Moderado"]["atual_valor"]
                            < alocacao_dict["Moderado"]["ideal_valor"]
                        ):
                            recomendacoes.append(
                                f"- **Realocação Baixo → Moderado**: Transfira **R$ {excesso_baixo:,.2f}** dos investimentos de risco **Baixo** para **Moderado**".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", ".")
                            )

                    if (
                        "Moderado" in alocacao_dict
                        and alocacao_dict["Moderado"]["atual_valor"]
                        > alocacao_dict["Moderado"]["ideal_valor"]
                    ):
                        excesso_moderado = (
                            alocacao_dict["Moderado"]["atual_valor"]
                            - alocacao_dict["Moderado"]["ideal_valor"]
                        )
                        if (
                            "Alto" in alocacao_dict
                            and alocacao_dict["Alto"]["atual_valor"]
                            < alocacao_dict["Alto"]["ideal_valor"]
                        ):
                            recomendacoes.append(
                                f"- **Realocação Moderado → Alto**: Transfira **R$ {excesso_moderado:,.2f}** dos investimentos de risco **Moderado** para **Alto**".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", ".")
                            )

                    # Verificar se Alto precisa de mais investimento
                    if (
                        "Alto" in alocacao_dict
                        and alocacao_dict["Alto"]["atual_valor"]
                        < alocacao_dict["Alto"]["ideal_valor"]
                    ):
                        falta_alto = (
                            alocacao_dict["Alto"]["ideal_valor"]
                            - alocacao_dict["Alto"]["atual_valor"]
                        )
                        # Verificar se já há recomendação para este caso
                        tem_recomendacao_alto = any(
                            "Alto" in rec and "→" in rec for rec in recomendacoes
                        )
                        if not tem_recomendacao_alto:
                            recomendacoes.append(
                                f"- **Aumentar Alto**: Invista mais **R$ {falta_alto:,.2f}** em ativos de risco **Alto**".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", ".")
                            )

                # Exibir as recomendações
                st.subheader("📋 Análise da Carteira")

                # Exibir situação atual vs. ideal em formato de tabela para facilitar visualização
                dados_tabela = []
                for perfil in ["Baixo", "Moderado", "Alto"]:
                    if perfil in alocacao_dict:
                        dados_tabela.append(
                            {
                                "Perfil": perfil,
                                "Alocação Atual": f"{alocacao_dict[perfil]['atual_perc']:.1f}%",
                                "Alocação Ideal": f"{alocacao_dict[perfil]['ideal_perc']:.1f}%",
                                "Valor Atual": f"R$ {alocacao_dict[perfil]['atual_valor']:,.2f}".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", "."),
                                "Valor Ideal": f"R$ {alocacao_dict[perfil]['ideal_valor']:,.2f}".replace(
                                    ",", "X"
                                )
                                .replace(".", ",")
                                .replace("X", "."),
                            }
                        )

                st.table(pd.DataFrame(dados_tabela))

                st.subheader("🔄 Recomendações de Realocação")
                if recomendacoes:
                    for rec in recomendacoes:
                        st.markdown(rec)
                else:
                    st.info(
                        "Não há recomendações específicas de realocação. Sua carteira está próxima do ideal para seu perfil."
                    )
        with tab2:
            # Calcular total investido original para alocação ideal
            total_investido_original = df_investimentos["valor_investido"].sum()
            
            # Recalcular alocação ideal com base no total investido original
            # (apenas se ainda não foi calculado na aba Comparativo)
            if 'alocacao_ideal_recalculada' not in locals():
                alocacao_ideal_recalculada = calcular_alocacao_ideal(perfil_cliente, total_investido_original)
                
            col1, col2 = st.columns(2)
            # Gráfico de pizza da composição atual (baseado nos valores atuais)
            fig_pizza_atual = criar_grafico_pizza(alocacao_atual_corrigida)
            col1.plotly_chart(fig_pizza_atual, use_container_width=True)

            # Gráfico de pizza da composição ideal (baseado na alocação ideal recalculada)
            fig_pizza_ideal = criar_grafico_pizza_ideal(alocacao_ideal_recalculada)
            col2.plotly_chart(fig_pizza_ideal, use_container_width=True)

        with tab3:
            # Filtros
            col1, col2 = st.columns(2)

            with col1:
                tipo_filtro = st.selectbox(
                    "Tipo de Investimento", ["Todos", "Fundo", "Cripto", "Ações"]
                )

            with col2:
                # Preparar datas para o filtro
                # Criar uma cópia explícita para evitar SettingWithCopyWarning
                df_investimentos = df_investimentos.copy()
                df_investimentos.loc[:, "data_aplicacao"] = pd.to_datetime(
                    df_investimentos["data_aplicacao"]
                )
                min_date = df_investimentos["data_aplicacao"].min().date()
                max_date = datetime.now().date()

                # Usar a data atual como valor padrão para que o calendário abra mostrando o mês atual
                data_filtro = st.date_input(
                    "Período",
                    [
                        min_date,
                        max_date,
                    ],
                    min_value=min_date,
                    max_value=max_date,
                )

            # Adicionar lógica para gerar 3 tabelas quando selecionado 'todos' e atualizar individualmente
            if tipo_filtro == "Todos":
                df_fundos = df_investimentos[df_investimentos["tipo"] == "Fundo"]
                # Carregar diretamente do banco para ter acesso a todas as colunas necessárias
                _, _, _, _, _, df_cripto_original, df_acoes_original = get_all_dataframes()

                # Filtrar apenas as criptomoedas relevantes baseado nos investimentos
                ids_cripto = df_investimentos[df_investimentos["tipo"] == "Cripto"][
                    "id"
                ].tolist()
                df_cripto = df_cripto_original[
                    df_cripto_original["id_cripto"].isin(ids_cripto)
                ].copy()

                # Calcular meses decorridos para cada investimento
                # Criar uma cópia explícita para evitar SettingWithCopyWarning
                df_fundos = df_fundos.copy()
                df_fundos.loc[:, "data_aplicacao"] = pd.to_datetime(
                    df_fundos["data_aplicacao"]
                )
                hoje = datetime.now()
                df_fundos.loc[:, "meses_decorridos"] = df_fundos["data_aplicacao"].apply(
                    lambda x: (hoje.year - x.year) * 12 + (hoje.month - x.month)
                )

                # Cálculo usando juros compostos, exatamente igual ao da função obter_investimentos_cliente()
                df_fundos.loc[:, "valor_atual"] = df_fundos.apply(
                    lambda x: x["valor_investido"]
                    * (1 + x["rentabilidade"]) ** x["meses_decorridos"],
                    axis=1,
                )

                # Calcular variação percentual
                df_fundos.loc[:, "variacao"] = (
                    df_fundos["valor_atual"] / df_fundos["valor_investido"] - 1
                ) * 100

                # Gerar tabelas conforme seleção
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("Fundos")
                    # Selecionar apenas as colunas solicitadas
                    tabela_fundos = df_fundos[
                        [
                            "nome",
                            "valor_investido",
                            "valor_atual",
                        ]
                    ]
                    
                    # Renomear colunas para melhor acessibilidade
                    tabela_fundos = tabela_fundos.rename(columns={
                        "nome": "Nome",
                        "valor_investido": "Valor Investido (BR)",
                        "valor_atual": "Valor Atual (BR)",
                    })

                    # Formatar valores
                    tabela_fundos_formatted = tabela_fundos.style.format(
                        {
                            "Valor Investido (BR)": "R$ {:.2f}",
                            "Valor Atual (BR)": "R$ {:.2f}",
                        }
                    )

                    # Exibir tabela sem índices
                    st.dataframe(
                        tabela_fundos_formatted,
                        use_container_width=True,
                        hide_index=True,
                    )
                with col2:
                    st.write("Criptos")
                    # Importar a função get_current_prices para atualizar os preços
                    from etl.criptomoedas import get_current_prices

                    # Criar uma cópia segura do DataFrame
                    cripto_df = df_cripto.copy(deep=True)

                    # Atualizar preços e calcular variações
                    cripto_df = get_current_prices(cripto_df)

                    # Calcular valor atual usando .loc para evitar SettingWithCopyWarning
                    cripto_df.loc[:, "valor_atual"] = (
                        cripto_df["valor_investido_br"] / cripto_df["preco_compra_br"]
                    ) * cripto_df["preco_atual_br"]
                    tabela_cripto = cripto_df[
                        [
                            "nome",
                            "valor_investido_br",
                            "valor_atual",
                        ]
                    ]
                    
                    # Renomear colunas para melhor acessibilidade
                    tabela_cripto = tabela_cripto.rename(columns={
                        "nome": "Nome",
                        "valor_investido_br": "Valor Investido (BR)",
                        "valor_atual": "Valor Atual (BR)",
                    })
                    tabela_cripto_formatted = tabela_cripto.style.format(
                        {
                            "Valor Investido (BR)": "R$ {:.2f}",
                            "Valor Atual (BR)": "R$ {:.2f}",
                        }
                    )
                    st.dataframe(
                        tabela_cripto_formatted,
                        use_container_width=True,
                        hide_index=True,
                    )
                with col3:
                    st.write("Ações")
                    # Filtrar apenas as ações relevantes baseado nos investimentos
                    ids_acoes = df_investimentos[df_investimentos["tipo"] == "Ações"][
                        "id"
                    ].tolist()
                    df_acoes = df_acoes_original[
                        df_acoes_original["id_acoes"].isin(ids_acoes)
                    ].copy()

                    # Importar a função get_current_prices_acoes para atualizar os preços
                    from etl.acoes import get_current_prices_acoes

                    # Criar uma cópia segura do DataFrame
                    acoes_df = df_acoes.copy(deep=True)

                    # Atualizar preços e calcular variações
                    acoes_df = get_current_prices_acoes(acoes_df)

                    # Calcular valor atual
                    acoes_df.loc[:, "valor_atual"] = (
                        acoes_df["quantidade"] * acoes_df["preco_atual_br"]
                    )

                    # Selecionar colunas para exibição
                    tabela_acoes = acoes_df[
                        [
                            "nome",
                            "valor_investido_br",
                            "valor_atual",
                        ]
                    ]
                    
                    # Renomear colunas para melhor acessibilidade
                    tabela_acoes = tabela_acoes.rename(columns={
                        "nome": "Nome",
                        "valor_investido_br": "Valor Investido (BR)",
                        "valor_atual": "Valor Atual (BR)",
                    })

                    # Formatar valores
                    tabela_acoes_formatted = tabela_acoes.style.format(
                        {
                            "Valor Investido (BR)": "R$ {:.2f}",
                            "Valor Atual (BR)": "R$ {:.2f}",
                        }
                    )

                    st.dataframe(
                        tabela_acoes_formatted,
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                # Inicializar variável de controle
                mostrar_tabela_padrao = True

                # Aplicar filtros
                df_filtrado = df_investimentos.copy()

                # Filtro por tipo
                if tipo_filtro != "Todos":
                    df_filtrado = df_filtrado[df_filtrado["tipo"] == tipo_filtro]

                    # Se o tipo for Cripto, usar a mesma lógica da aba Detalhes
                    if tipo_filtro == "Cripto":
                        # Carregar diretamente do banco para ter acesso a todas as colunas necessárias
                        _, _, _, _, _, df_cripto_original, _ = get_all_dataframes()

                        # Filtrar apenas as criptomoedas relevantes baseado nos investimentos
                        ids_cripto = df_filtrado["id"].tolist()
                        df_cripto = df_cripto_original[
                            df_cripto_original["id_cripto"].isin(ids_cripto)
                        ].copy()

                        # Importar a função get_current_prices para atualizar os preços
                        from etl.criptomoedas import get_current_prices

                        # Criar uma cópia segura do DataFrame
                        cripto_df = df_cripto.copy(deep=True)

                        # Atualizar preços e calcular variações
                        cripto_df = get_current_prices(cripto_df)

                        # Calcular valor atual usando .loc para evitar SettingWithCopyWarning
                        cripto_df.loc[:, "valor_atual"] = (
                            cripto_df["valor_investido_br"]
                            / cripto_df["preco_compra_br"]
                        ) * cripto_df["preco_atual_br"]

                        # Selecionar colunas para exibição
                        tabela_cripto = cripto_df[
                            [
                                "nome",
                                "valor_investido_br",
                                "preco_compra_br",
                                "preco_atual_br",
                                "variacao_percentual_br",
                                "valor_atual",
                                "data_aplicacao",
                                "perfil_risco",
                            ]
                        ]
                        
                        # Renomear colunas para melhor acessibilidade
                        tabela_cripto = tabela_cripto.rename(columns={
                            "nome": "Nome",
                            "valor_investido_br": "Valor Investido (BR)",
                            "preco_compra_br": "Preço de Compra (BR)",
                            "preco_atual_br": "Preço Atual (BR)",
                            "variacao_percentual_br": "Variação Percentual",
                            "valor_atual": "Valor Atual (BR)",
                            "data_aplicacao": "Data de Aplicação",
                            "perfil_risco": "Perfil de Risco",
                        })

                        # Formatar valores
                        tabela_cripto_formatted = tabela_cripto.style.format(
                            {
                                "Valor Investido (BR)": "R$ {:.2f}",
                                "Preço de Compra (BR)": "R$ {:.2f}",
                                "Preço Atual (BR)": "R$ {:.2f}",
                                "Variação Percentual": "{:.2f}%",
                                "Valor Atual (BR)": "R$ {:.2f}",
                            }
                        )

                        # Exibir a tabela formatada
                        st.dataframe(
                            tabela_cripto_formatted,
                            use_container_width=True,
                            hide_index=True,
                        )

                        # Definir variável de controle para evitar a exibição da tabela padrão
                        mostrar_tabela_padrao = False

                    # Se o tipo for Ações, usar a mesma lógica da aba Detalhes
                    elif tipo_filtro == "Ações":
                        # Carregar diretamente do banco para ter acesso a todas as colunas necessárias
                        _, _, _, _, _, _, df_acoes_original = get_all_dataframes()

                        # Filtrar apenas as ações relevantes baseado nos investimentos
                        ids_acoes = df_filtrado["id"].tolist()
                        df_acoes = df_acoes_original[
                            df_acoes_original["id_acoes"].isin(ids_acoes)
                        ].copy()

                        # Importar a função get_current_prices_acoes para atualizar os preços
                        from etl.acoes import get_current_prices_acoes

                        # Criar uma cópia segura do DataFrame
                        acoes_df = df_acoes.copy(deep=True)

                        # Atualizar preços e calcular variações
                        acoes_df = get_current_prices_acoes(acoes_df)

                        # Calcular valor atual
                        acoes_df.loc[:, "valor_atual"] = (
                            acoes_df["quantidade"] * acoes_df["preco_atual_br"]
                        )

                        # Selecionar colunas para exibição
                        tabela_acoes = acoes_df[
                            [
                                "nome",
                                "quantidade",
                                "valor_investido_br",
                                "preco_compra_br",
                                "preco_atual_br",
                                "variacao_percentual_br",
                                "valor_atual",
                                "data_aplicacao",
                                "perfil_risco",
                            ]
                        ]
                        
                        # Renomear colunas para melhor acessibilidade
                        tabela_acoes = tabela_acoes.rename(columns={
                            "nome": "Nome",
                            "quantidade": "Quantidade",
                            "valor_investido_br": "Valor Investido (BR)",
                            "preco_compra_br": "Preço de Compra (BR)",
                            "preco_atual_br": "Preço Atual (BR)",
                            "variacao_percentual_br": "Variação Percentual",
                            "valor_atual": "Valor Atual (BR)",
                            "data_aplicacao": "Data de Aplicação",
                            "perfil_risco": "Perfil de Risco",
                        })

                        # Formatar valores
                        tabela_acoes_formatted = tabela_acoes.style.format(
                            {
                                "Valor Investido (BR)": "R$ {:.2f}",
                                "Preço de Compra (BR)": "R$ {:.2f}",
                                "Preço Atual (BR)": "R$ {:.2f}",
                                "Variação Percentual": "{:.2f}%",
                                "Valor Atual (BR)": "R$ {:.2f}",
                            }
                        )

                        # Exibir a tabela formatada
                        st.dataframe(
                            tabela_acoes_formatted,
                            use_container_width=True,
                            hide_index=True,
                        )

                        # Definir variável de controle para evitar a exibição da tabela padrão
                        mostrar_tabela_padrao = False

                # Filtro por data
                if len(data_filtro) == 2:
                    data_inicio, data_fim = data_filtro
                    
                    # Converter as datas para timestamp para comparação
                    data_inicio_ts = pd.Timestamp(data_inicio)
                    data_fim_ts = pd.Timestamp(data_fim)
                    
                    # Filtrar usando timestamp
                    df_filtrado = df_filtrado.copy()
                    # Garantir que data_aplicacao seja datetime
                    df_filtrado.loc[:, "data_aplicacao"] = pd.to_datetime(df_filtrado["data_aplicacao"])
                    
                    # Filtrar usando comparação de timestamps
                    df_filtrado = df_filtrado[
                        (df_filtrado["data_aplicacao"] >= data_inicio_ts) &
                        (df_filtrado["data_aplicacao"] <= data_fim_ts)
                    ]

                # Inicializar df_exibicao para evitar erro de variável não definida
                df_exibicao = None

                # Verificar se devemos mostrar a tabela padrão
                if mostrar_tabela_padrao:
                    # Formatar tabela para exibição
                    df_exibicao = df_filtrado.copy()

                    # Formatar colunas para exibição
                    # Criar uma cópia explícita para evitar SettingWithCopyWarning
                    df_exibicao = df_exibicao.copy()
                    
                    # Formatar a data sem depender do atributo .dt
                    # Primeiro, verificamos se a coluna já é datetime
                    try:
                        # Tentar converter para datetime e depois para string no formato desejado
                        df_exibicao.loc[:, "data_aplicacao"] = pd.to_datetime(df_exibicao["data_aplicacao"]).dt.strftime("%d/%m/%Y")
                    except AttributeError:
                        # Se falhar, usar uma abordagem alternativa com apply
                        df_exibicao.loc[:, "data_aplicacao"] = df_exibicao["data_aplicacao"].apply(
                            lambda x: pd.to_datetime(x).strftime("%d/%m/%Y") if pd.notna(x) else ""
                        )
                    
                    df_exibicao.loc[:, "valor_investido"] = df_exibicao[
                        "valor_investido"
                    ].apply(
                        lambda x: f"R$ {x:,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )
                    
                    df_exibicao.loc[:, "valor_atual"] = df_exibicao["valor_atual"].apply(
                        lambda x: f"R$ {x:,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )
                    
                    df_exibicao.loc[:, "rentabilidade"] = df_exibicao["rentabilidade"].apply(
                        lambda x: f"{x * 100:.2f}%"
                    )

                    # Adicionar a variação percentual
                    df_exibicao.loc[:, "Variação"] = df_filtrado.apply(
                        lambda x: f"{((x['valor_atual'] / x['valor_investido']) - 1) * 100:.2f}%",
                        axis=1,
                    )

                    # Renomear colunas para exibição
                    df_exibicao = df_exibicao.rename(
                        columns={
                            "nome": "Nome",
                            "tipo": "Tipo",
                            "valor_investido": "Valor Investido (BR)",
                            "valor_atual": "Valor Atual (BR)",
                            "perfil_risco": "Perfil de Risco",
                            "rentabilidade": "Rentabilidade",
                            "data_aplicacao": "Data de Aplicação",
                        }
                    )

                    # Selecionar e reordenar colunas para exibição
                    df_exibicao = df_exibicao[
                        [
                            "Nome",
                            "Tipo",
                            "Valor Investido (BR)",
                            "Valor Atual (BR)",
                            "Variação",
                            "Perfil de Risco",
                            "Rentabilidade",
                            "Data de Aplicação",
                        ]
                    ]

                    # Exibir tabela
                    st.dataframe(df_exibicao, use_container_width=True)

# Adicionar o footer
add_footer()
