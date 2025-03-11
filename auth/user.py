import requests
import streamlit as st


def authenticate_user(cpf, senha):
    """
    Função para autenticar o usuário na API e obter o token.

    Args:
        cpf (str): CPF do usuário.
        senha (str): Senha do usuário.

    Returns:
        str: Token de autenticação se a autenticação for bem-sucedida.
        None caso contrário.
    """
    try:
        response = requests.post(
            "https://vs15-internet-banking-back.onrender.com/auth",
            json={"cpf": cpf, "senha": senha},
        )
        response.raise_for_status()  # Lança uma exceção para status de erro
        token = response.json().get("token")
        if token:
            # Armazenar o token na sessão do Streamlit
            st.session_state.token = token
            return token
        else:
            print("Erro: Token não encontrado na resposta.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao autenticar usuário: {e}")
        return None


def get_logged_user():
    """Obtém os dados do usuário logado através do token.

    Returns:
        dict: Dados do usuário logado ou None se ocorrer um erro.
    """
    try:
        token = st.session_state.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://vs15-internet-banking-back.onrender.com/conta/logado",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None


def get_user_cpf():
    """Obtém o CPF do usuário logado através do token.

    Returns:
        str: CPF do usuário logado ou None se ocorrer um erro.
    """
    try:
        token = st.session_state.get("token")
        if not token:
            return None

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://vs15-internet-banking-back.onrender.com/conta/logado",
            headers=headers,
        )
        response.raise_for_status()
        user_data = response.json()

        # A resposta tem o formato: {"pessoa": {"usuario": {"cpf": "string"}}}
        if user_data and "pessoa" in user_data and user_data["pessoa"]:
            pessoa = user_data["pessoa"]
            if "usuario" in pessoa and pessoa["usuario"]:
                usuario = pessoa["usuario"]
                return usuario.get("cpf")

        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter CPF do usuário: {e}")
        return None


def get_user_data_by_cpf(cpf):
    """Obtém todos os dados do usuário a partir do CPF.

    Args:
        cpf (str): CPF do usuário.

    Returns:
        dict: Dicionário com todas as informações do usuário:
            - dados_usuario: Informações da tabela usuario
            - dados_pessoa: Informações da tabela pessoa
            - contas: Lista de contas do usuário
            - id_conta: ID da conta principal do usuário
    """
    try:
        # Importar funções do módulo db.db
        from db.db import (
            get_usuario_by_cpf_senha,
            get_pessoa_by_id_usuario,
            get_contas_by_id_pessoa
        )
        
        token = st.session_state.get("token")
        if not token:
            print("Token não encontrado na sessão.")
            return None

        headers = {"Authorization": f"Bearer {token}"}

        # Tentar obter dados diretamente da conta logada primeiro para obter o CPF
        try:
            response_conta = requests.get(
                "https://vs15-internet-banking-back.onrender.com/conta/logado",
                headers=headers,
            )
            response_conta.raise_for_status()
            dados_conta = response_conta.json()

            # Extrair dados da pessoa e usuário da conta logada
            if dados_conta and "pessoa" in dados_conta:
                dados_pessoa_api = dados_conta["pessoa"]
                dados_usuario_api = dados_pessoa_api.get("usuario", {})

                # Verificar se o CPF corresponde
                if dados_usuario_api.get("cpf") == cpf:
                    # Agora vamos buscar os dados no banco de dados local usando o CPF
                    df_usuario = get_usuario_by_cpf_senha(cpf, None)
                    
                    if df_usuario.empty:
                        print(f"Usuário com CPF {cpf} não encontrado no banco de dados.")
                        # Usar os dados da API como fallback
                        return {
                            "dados_usuario": dados_usuario_api,
                            "dados_pessoa": dados_pessoa_api,
                            "contas": [dados_conta],
                            "id_conta": dados_conta.get("idConta"),
                        }
                    
                    # Obter dados do banco de dados
                    id_usuario = df_usuario.iloc[0]["id_usuario"]
                    df_pessoa = get_pessoa_by_id_usuario(id_usuario)
                    
                    if df_pessoa.empty:
                        print(f"Pessoa para o usuário com ID {id_usuario} não encontrada no banco de dados.")
                        # Usar os dados da API como fallback
                        return {
                            "dados_usuario": dados_usuario_api,
                            "dados_pessoa": dados_pessoa_api,
                            "contas": [dados_conta],
                            "id_conta": dados_conta.get("idConta"),
                        }
                    
                    id_pessoa = df_pessoa.iloc[0]["id_pessoa"]
                    df_contas = get_contas_by_id_pessoa(id_pessoa)
                    
                    # Converter DataFrames para dicionários
                    dados_usuario = df_usuario.iloc[0].to_dict()
                    dados_pessoa = df_pessoa.iloc[0].to_dict()
                    contas = [row.to_dict() for _, row in df_contas.iterrows()]
                    
                    # Usar o ID da primeira conta como ID principal (ou o ID da API se não houver contas)
                    id_conta = contas[0]["id_conta"] if contas else dados_conta.get("idConta")
                    
                    return {
                        "dados_usuario": dados_usuario,
                        "dados_pessoa": dados_pessoa,
                        "contas": contas,
                        "id_conta": id_conta,
                    }
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter dados da conta logada: {e}")
            return None
    except Exception as e:
        print(f"Erro ao obter dados do usuário por CPF: {e}")
        return None
