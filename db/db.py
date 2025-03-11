"""
Módulo para conexão com o banco de dados PostgreSQL
"""

import pandas as pd
import sqlalchemy as sa
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Dados de conexão (lidos do .env)
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Verifica se todas as variáveis foram carregadas com sucesso
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Variáveis de ambiente não configuradas corretamente no arquivo .env")

# Criação da URL de conexão
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Criação da engine
engine = sa.create_engine(DATABASE_URL)


# Funções para consultar as tabelas
def get_all_from_table(table_name):
    """
    Retorna todos os registros de uma tabela específica como DataFrame
    """
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)


def get_usuario_by_cpf_senha(cpf, senha=None):
    """
    Retorna um usuário com base no CPF e, opcionalmente, senha
    
    Se a senha for fornecida, tenta autenticar o usuário na API.
    Se a senha não for fornecida, apenas busca o usuário no banco de dados pelo CPF.
    """
    if senha:
        # Importa a função de autenticação do módulo auth.user
        from auth.user import authenticate_user

        # Autentica o usuário usando o CPF e senha
        token = authenticate_user(cpf, senha)

        # Se o usuário for autenticado com sucesso, busca seus dados no banco
        if token:
            # Buscar o usuário no banco de dados pelo CPF
            query = "SELECT * FROM usuario WHERE cpf = %(cpf)s"
            return pd.read_sql(query, engine, params={"cpf": cpf})
    else:
        # Se não foi fornecida senha, apenas busca o usuário pelo CPF
        query = "SELECT * FROM usuario WHERE cpf = %(cpf)s"
        return pd.read_sql(query, engine, params={"cpf": cpf})

    # Se a autenticação falhar ou o usuário não for encontrado, retorna um DataFrame vazio
    return pd.DataFrame()


def get_pessoa_by_id_usuario(id_usuario):
    """
    Retorna uma pessoa com base no ID do usuário
    """
    # Converter o id_usuario para um tipo Python nativo (int)
    id_usuario_int = int(id_usuario)
    
    query = """
    SELECT * FROM pessoa 
    WHERE id_usuario = %(id_usuario)s
    """
    return pd.read_sql(query, engine, params={"id_usuario": id_usuario_int})


def get_contas_by_id_pessoa(id_pessoa):
    """
    Retorna as contas de uma pessoa com base no ID da pessoa
    """
    # Converter o id_pessoa para um tipo Python nativo (int)
    id_pessoa_int = int(id_pessoa)
    
    query = """
    SELECT * FROM conta 
    WHERE id_pessoa = %(id_pessoa)s
    """
    return pd.read_sql(query, engine, params={"id_pessoa": id_pessoa_int})


def get_investimentos_by_id_conta(id_conta):
    """
    Retorna os investimentos de uma conta com base no ID da conta
    """
    # Converter o id_conta para um tipo Python nativo (int)
    id_conta_int = int(id_conta)
    
    query = """
    SELECT * FROM containvestimento 
    WHERE id_conta = %(id_conta)s
    """
    return pd.read_sql(query, engine, params={"id_conta": id_conta_int})


def get_fundos_by_id_investimento(id_investimento):
    """
    Retorna os fundos de investimento com base no ID do investimento
    """
    # Converter o id_investimento para um tipo Python nativo (int)
    id_investimento_int = int(id_investimento)
    
    query = """
    SELECT * FROM fundoinvestimento 
    WHERE id_investimento = %(id_investimento)s
    """
    return pd.read_sql(query, engine, params={"id_investimento": id_investimento_int})


def get_criptos_by_id_investimento(id_investimento):
    """
    Retorna os investimentos em criptomoedas com base no ID do investimento
    """
    # Converter o id_investimento para um tipo Python nativo (int)
    id_investimento_int = int(id_investimento)
    
    query = """
    SELECT * FROM investimentos_cripto 
    WHERE id_investimento = %(id_investimento)s
    """
    return pd.read_sql(query, engine, params={"id_investimento": id_investimento_int})


def get_acoes_by_id_investimento(id_investimento):
    """
    Retorna as ações com base no ID do investimento
    """
    # Converter o id_investimento para um tipo Python nativo (int)
    id_investimento_int = int(id_investimento)
    
    query = """
    SELECT * FROM acoes 
    WHERE id_investimento = %(id_investimento)s
    """
    return pd.read_sql(query, engine, params={"id_investimento": id_investimento_int})


def get_all_dataframes():
    """
    Retorna todos os dados das tabelas como DataFrames Pandas
    """
    df_usuario = get_all_from_table("usuario")
    df_pessoa = get_all_from_table("pessoa")
    df_conta = get_all_from_table("conta")
    df_containvestimento = get_all_from_table("containvestimento")
    df_fundoinvestimento = get_all_from_table("fundoinvestimento")
    df_investimentos_cripto = get_all_from_table("investimentos_cripto")
    df_acoes = get_all_from_table("acoes")

    return (
        df_usuario,
        df_pessoa,
        df_conta,
        df_containvestimento,
        df_fundoinvestimento,
        df_investimentos_cripto,
        df_acoes,
    )
