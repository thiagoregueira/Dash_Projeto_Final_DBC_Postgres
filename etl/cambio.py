import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import os


def baixar_historico_cambio():
    """
    Baixa o histórico dos últimos 10 anos das principais moedas em relação ao Real
    e salva em um arquivo CSV.
    """
    try:
        # Lista das principais moedas (em relação ao Real)
        moedas = {
            "USDBRL=X": "Dólar Americano",
            "EURBRL=X": "Euro",
            "GBPBRL=X": "Libra Esterlina",
            "JPYBRL=X": "Iene Japonês",
            "CHFBRL=X": "Franco Suíço",
            "CNYBRL=X": "Yuan Chinês",
            "AUDBRL=X": "Dólar Australiano",
            "CADBRL=X": "Dólar Canadense",
        }

        # Data inicial (10 anos atrás)
        data_inicial = (datetime.now() - timedelta(days=3650)).strftime("%Y-%m-%d")

        # Lista para armazenar todos os dados históricos
        dados_historicos = []

        print("Iniciando download do histórico das moedas...")

        # Processa cada moeda
        for simbolo, nome in moedas.items():
            try:
                # Obtém dados históricos da moeda
                moeda = yf.Ticker(simbolo)
                hist = moeda.history(start=data_inicial)

                if hist.empty:
                    continue

                # Adiciona informações ao histórico
                hist["Simbolo"] = simbolo
                hist["Nome"] = nome

                # Reseta o índice para transformar a data em coluna
                hist = hist.reset_index()
                hist["Date"] = hist["Date"].dt.strftime("%Y-%m-%d")

                # Adiciona aos dados históricos
                dados_historicos.append(hist)

                print(f"Dados baixados para {nome} ({simbolo})")

                # Pausa para evitar sobrecarga na API
                time.sleep(1)

            except Exception as e:
                print(f"Erro ao baixar dados de {simbolo}: {str(e)}")
                continue

        # Combina todos os dados históricos
        if dados_historicos:
            df_historico = pd.concat(dados_historicos, ignore_index=True)

            # Seleciona e renomeia as colunas relevantes
            df_historico = df_historico[["Date", "Simbolo", "Nome", "Close"]]
            df_historico.columns = ["Data", "Simbolo", "Nome_Moeda", "Preco"]

            # Calcula a variação diária
            df_historico["Variacao"] = (
                df_historico.groupby("Simbolo")["Preco"].pct_change() * 100
            )

            # Determinar o caminho base do projeto
            if os.path.exists("results"):
                base_path = ""
            else:
                base_path = ".."

            # Salva o histórico em CSV
            nome_arquivo = os.path.join(base_path, "results", "historico_cambio.csv")
            df_historico.to_csv(nome_arquivo, index=False)
            print("\nHistórico salvo com sucesso em 'historico_cambio.csv'")

            return df_historico
        else:
            print("\nNenhum dado histórico foi baixado")
            return pd.DataFrame()

    except Exception as e:
        print(f"Erro ao processar dados históricos: {str(e)}")
        return pd.DataFrame()


def obter_variacao_cambio(periodo="1d"):
    """
    Obtém a variação das moedas no período especificado.

    Args:
        periodo (str): Período de análise ('1d' para 30 dias, '1mo' para mensal, '1y' para anual)
    """
    try:
        # Lê o arquivo CSV com o histórico
        # Determinar o caminho base do projeto
        if os.path.exists("results"):
            base_path = ""
        else:
            base_path = ".."

        nome_arquivo = os.path.join(base_path, "results", "historico_cambio.csv")
        df_historico = pd.read_csv(nome_arquivo)
        df_historico["Data"] = pd.to_datetime(df_historico["Data"])

        # Obtém a data mais recente
        data_mais_recente = df_historico["Data"].max()

        # Filtra e agrega dados conforme o período
        if periodo == "1d":
            # Últimos 30 dias
            data_inicio = data_mais_recente - pd.Timedelta(days=30)
            df_periodo = df_historico[df_historico["Data"] >= data_inicio].copy()
            df_periodo = (
                df_periodo.groupby("Simbolo")
                .agg({"Preco": ["first", "last"], "Nome_Moeda": "first"})
                .reset_index()
            )
            df_periodo.columns = [
                "Simbolo",
                "Preco_Inicial",
                "Preco_Final",
                "Nome_Moeda",
            ]

        elif periodo == "1mo":
            # Agregar por mês
            df_historico["Mes_Ano"] = df_historico["Data"].dt.to_period("M")
            df_periodo = (
                df_historico.groupby(["Simbolo", "Mes_Ano", "Nome_Moeda"])["Preco"]
                .mean()
                .reset_index()
            )
            df_periodo = df_periodo.sort_values(["Simbolo", "Mes_Ano"])
            df_periodo = (
                df_periodo.groupby("Simbolo")
                .agg({"Preco": ["first", "last"], "Nome_Moeda": "first"})
                .reset_index()
            )
            df_periodo.columns = [
                "Simbolo",
                "Preco_Inicial",
                "Preco_Final",
                "Nome_Moeda",
            ]

        else:  # '1y'
            # Agregar por ano
            df_historico["Ano"] = df_historico["Data"].dt.year
            df_periodo = (
                df_historico.groupby(["Simbolo", "Ano", "Nome_Moeda"])["Preco"]
                .mean()
                .reset_index()
            )
            df_periodo = df_periodo.sort_values(["Simbolo", "Ano"])
            df_periodo = (
                df_periodo.groupby("Simbolo")
                .agg({"Preco": ["first", "last"], "Nome_Moeda": "first"})
                .reset_index()
            )
            df_periodo.columns = [
                "Simbolo",
                "Preco_Inicial",
                "Preco_Final",
                "Nome_Moeda",
            ]

        # Calcula a variação percentual
        df_periodo["Variacao"] = (
            (df_periodo["Preco_Final"] / df_periodo["Preco_Inicial"]) - 1
        ) * 100

        if df_periodo.empty:
            return pd.DataFrame()

        # Formata os dados para exibição
        df_periodo["Preço"] = df_periodo["Preco_Final"].round(
            4
        )  # 4 casas decimais para câmbio
        df_periodo["Variação (%)"] = df_periodo["Variacao"].round(2)
        df_periodo["Símbolo"] = df_periodo["Simbolo"]
        df_periodo["Nome"] = df_periodo["Nome_Moeda"]

        # Retorna todas as moedas ordenadas por variação
        return df_periodo[["Símbolo", "Nome", "Preço", "Variação (%)"]].sort_values(
            "Variação (%)", ascending=False
        )

    except Exception as e:
        print(f"Erro ao obter variação do câmbio: {str(e)}")
        return pd.DataFrame()


def get_usdbrl_rate():
    try:
        usdbrl = yf.Ticker("USDBRL=X")
        hist = usdbrl.history(period="1d", interval="1m")
        return hist["Close"].iloc[-1]
    except Exception as e:
        print(f"Erro ao buscar taxa USD/BRL: {e}")
        return 5.0
