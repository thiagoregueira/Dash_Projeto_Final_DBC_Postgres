import pandas as pd
from datetime import datetime
import os
import chardet


def processar_ibrx50():
    # Obter a data atual no formato dd-mm-yy
    data_atual = datetime.now().strftime("%d-%m-%y")

    # Construir o nome do arquivo
    # Determinar o caminho base do projeto
    if os.path.exists("results"):
        base_path = ""
    else:
        base_path = ".."

    nome_arquivo = os.path.join(base_path, "results", f"IBXLDia_{data_atual}.csv")

    # Verificar se o arquivo existe
    if not os.path.exists(nome_arquivo):
        raise FileNotFoundError(f"Arquivo {nome_arquivo} não encontrado!")

    try:
        # Detectar o encoding do arquivo
        with open(nome_arquivo, "rb") as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result["encoding"]

        print(f"Encoding detectado: {encoding}")

        # Ler o arquivo linha por linha para tratar o ponto e vírgula extra
        with open(nome_arquivo, "r", encoding=encoding) as file:
            linhas = file.readlines()

        # Remover ponto e vírgula extra no final das linhas e espaços em branco
        linhas_limpas = [linha.strip().rstrip(";") + "\n" for linha in linhas]

        # Pegar apenas as linhas de dados (pulando o título e o cabeçalho)
        dados_acoes = linhas_limpas[2:]

        # Criar DataFrame a partir das linhas de dados
        df = pd.DataFrame([linha.strip().split(";") for linha in dados_acoes])

        # Definir os nomes das colunas
        df.columns = ["Código", "Ação", "Tipo", "Qtde. Teórica", "Part. (%)"]

        print("\nColunas do DataFrame:")
        print(df.columns.tolist())

        # Pegar apenas as 50 linhas que contém dados das ações (excluindo as 2 últimas linhas de totais)
        df = df.iloc[:50]

        # Converter a coluna de porcentagem para número
        try:
            df["Part. (%)"] = df["Part. (%)"].str.replace(",", ".").astype(float)
        except Exception as e:
            print("\nErro ao converter porcentagem:")
            print(f"Colunas disponíveis: {df.columns.tolist()}")
            print(f"Primeiras linhas do DataFrame:\n{df.head()}")
            raise e

        # Verificar duplicatas
        duplicatas = df.duplicated().sum()
        if duplicatas > 0:
            print(f"\nForam encontradas {duplicatas} linhas duplicadas")
            # Remover duplicatas
            df = df.drop_duplicates()
            print(f"Duplicatas removidas. Novo número de linhas: {len(df)}")
        else:
            print("\nNão foram encontradas duplicatas")

        # Selecionar apenas a coluna Código
        df_codigo = df[["Código"]]

        # Salvar o arquivo atualizado apenas com os códigos
        try:
            with open(nome_arquivo, "w", encoding="UTF-8") as file:
                # Escrever o título original
                file.write(f"IBXL - Carteira do Dia {data_atual}\n")

                # Escrever o cabeçalho
                file.write("Código\n")

                # Escrever as linhas de dados formatadas
                for codigo in df_codigo["Código"]:
                    file.write(f"{codigo}\n")

                print(
                    f"Arquivo salvo com sucesso apenas com os códigos: {nome_arquivo}"
                )
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {str(e)}")
            raise e

        # Exibir informações do DataFrame
        print(f"\nInformações do arquivo {nome_arquivo}:")
        print(f"Número de linhas: {len(df)}")
        print("\nPrimeiras 5 linhas do DataFrame:")
        print(df.head())

        return df

    except Exception as e:
        print(f"Erro ao processar o arquivo: {str(e)}")
        return None
