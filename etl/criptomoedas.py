import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from etl.cambio import get_usdbrl_rate
import time
import os


def baixar_historico_cripto():
    """
    Baixa o histórico dos últimos 10 anos das principais criptomoedas
    e salva em um arquivo CSV.
    """
    try:
        # Lista das principais criptomoedas (símbolo-USD)
        criptos = {
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum",
            "USDT-USD": "Tether",
            "BNB-USD": "Binance Coin",
            "SOL-USD": "Solana",
            "XRP-USD": "Ripple",
            "ADA-USD": "Cardano",
            "AVAX-USD": "Avalanche",
            "DOGE-USD": "Dogecoin",
            "DOT-USD": "Polkadot",
        }

        # Data inicial (10 anos atrás)
        data_inicial = (datetime.now() - timedelta(days=3650)).strftime("%Y-%m-%d")

        # Lista para armazenar todos os dados históricos
        dados_historicos = []

        print("Iniciando download do histórico das criptomoedas...")

        # Processa cada criptomoeda
        for simbolo, nome in criptos.items():
            try:
                # Obtém dados históricos da criptomoeda
                cripto = yf.Ticker(simbolo)
                hist = cripto.history(start=data_inicial)

                if hist.empty:
                    continue

                # Adiciona informações ao histórico
                hist["Simbolo"] = simbolo.replace("-USD", "")
                hist["Nome"] = nome

                # Reseta o índice para transformar a data em coluna
                hist = hist.reset_index()
                hist["Date"] = hist["Date"].dt.strftime("%Y-%m-%d")

                # Adiciona aos dados históricos
                dados_historicos.append(hist)

                print(f"Dados baixados para {simbolo}")

                # Pausa para evitar sobrecarga na API
                time.sleep(1)

            except Exception as e:
                print(f"Erro ao baixar dados de {simbolo}: {str(e)}")
                continue

        # Combina todos os dados históricos
        if dados_historicos:
            df_historico = pd.concat(dados_historicos, ignore_index=True)

            # Seleciona e renomeia as colunas relevantes
            df_historico = df_historico[["Date", "Simbolo", "Nome", "Close", "Volume"]]
            df_historico.columns = ["Data", "Simbolo", "Nome_Cripto", "Preco", "Volume"]

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
            nome_arquivo = os.path.join(
                base_path, "results", "historico_criptomoedas.csv"
            )
            df_historico.to_csv(nome_arquivo, index=False)
            print("\nHistórico salvo com sucesso em 'historico_criptomoedas.csv'")

            return df_historico
        else:
            print("\nNenhum dado histórico foi baixado")
            return pd.DataFrame()

    except Exception as e:
        print(f"Erro ao processar dados históricos: {str(e)}")
        return pd.DataFrame()


def obter_melhores_e_piores_cripto(periodo="1d"):
    """
    Obtém as 5 melhores e 5 piores criptomoedas do período especificado.

    Args:
        periodo (str): Período de análise ('1d' para 30 dias, '1mo' para mensal, '1y' para anual)
    """
    try:
        # Determinar o caminho base do projeto
        if os.path.exists("results"):
            base_path = ""
        else:
            base_path = ".."

        # Lê o arquivo CSV com o histórico
        nome_arquivo = os.path.join(base_path, "results", "historico_criptomoedas.csv")
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
                .agg({"Preco": ["first", "last"], "Nome_Cripto": "first"})
                .reset_index()
            )
            df_periodo.columns = [
                "Simbolo",
                "Preco_Inicial",
                "Preco_Final",
                "Nome_Cripto",
            ]

        elif periodo == "1mo":
            # Agregar por mês
            df_historico["Mes_Ano"] = df_historico["Data"].dt.to_period("M")
            df_periodo = (
                df_historico.groupby(["Simbolo", "Mes_Ano", "Nome_Cripto"])["Preco"]
                .mean()
                .reset_index()
            )
            df_periodo = df_periodo.sort_values(["Simbolo", "Mes_Ano"])
            df_periodo = (
                df_periodo.groupby("Simbolo")
                .agg({"Preco": ["first", "last"], "Nome_Cripto": "first"})
                .reset_index()
            )
            df_periodo.columns = [
                "Simbolo",
                "Preco_Inicial",
                "Preco_Final",
                "Nome_Cripto",
            ]

        else:  # '1y'
            # Agregar por ano
            df_historico["Ano"] = df_historico["Data"].dt.year
            df_periodo = (
                df_historico.groupby(["Simbolo", "Ano", "Nome_Cripto"])["Preco"]
                .mean()
                .reset_index()
            )
            df_periodo = df_periodo.sort_values(["Simbolo", "Ano"])
            df_periodo = (
                df_periodo.groupby("Simbolo")
                .agg({"Preco": ["first", "last"], "Nome_Cripto": "first"})
                .reset_index()
            )
            df_periodo.columns = [
                "Simbolo",
                "Preco_Inicial",
                "Preco_Final",
                "Nome_Cripto",
            ]

        # Calcula a variação percentual
        df_periodo["Variacao"] = (
            (df_periodo["Preco_Final"] / df_periodo["Preco_Inicial"]) - 1
        ) * 100

        if df_periodo.empty:
            return pd.DataFrame(), pd.DataFrame()

        # Formata os dados para exibição
        df_periodo["Preço"] = df_periodo["Preco_Final"].round(2)
        df_periodo["Variação (%)"] = df_periodo["Variacao"].round(2)
        df_periodo["Símbolo"] = df_periodo["Simbolo"]
        df_periodo["Nome"] = df_periodo["Nome_Cripto"]

        # Ordena por variação e seleciona as 5 melhores e piores
        melhores = df_periodo.nlargest(5, "Variacao")[
            ["Símbolo", "Nome", "Preço", "Variação (%)"]
        ]
        piores = df_periodo.nsmallest(5, "Variacao")[
            ["Símbolo", "Nome", "Preço", "Variação (%)"]
        ]

        return melhores, piores

    except Exception as e:
        print(f"Erro ao obter melhores e piores criptomoedas: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()


def get_current_prices(df):
    symbol_map = {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Tether": "USDT-USD",
        "Binance Coin": "BNB-USD",
        "Cardano": "ADA-USD",
        "Solana": "SOL-USD",
        "Avalanche": "AVAX-USD",
        "Dogecoin": "DOGE-USD",
        "Polkadot": "DOT-USD",
    }

    # Busca preço atual em USD
    df["preco_atual_us"] = df["nome"].apply(
        lambda x: yf.Ticker(symbol_map.get(x, "BTC-USD")).history(period="1d")["Close"].iloc[-1]
    )

    # Conversão para BRL
    df["preco_atual_br"] = df["preco_atual_us"] * get_usdbrl_rate()
    
    # Adiciona a coluna preco_compra_br se não existir
    if "preco_compra" in df.columns and "preco_compra_br" not in df.columns:
        # Converte o preço de compra para BRL se já não estiver em BRL
        df["preco_compra_br"] = df["preco_compra"] 
    elif "preco_compra_br" not in df.columns:
        # Se não tiver o preço de compra, usa o preço atual como referência
        df["preco_compra_br"] = df["preco_atual_br"]
    
    # Adiciona a coluna valor_investido_br se não existir
    if "valor_investido" in df.columns and "valor_investido_br" not in df.columns:
        # Usa o valor investido existente
        df["valor_investido_br"] = df["valor_investido"]
    elif "valor_investido_br" not in df.columns:
        # Se não tiver valor investido, cria um valor padrão (0)
        df["valor_investido_br"] = 0

    # Calcula variação percentual
    df["variacao_percentual_br"] = (
        (df["preco_atual_br"] - df["preco_compra_br"]) / df["preco_compra_br"] * 100
    ).round(2)

    return df
