import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from etl.cambio import get_usdbrl_rate

def baixar_historico_acoes():
    """
    Baixa o histórico dos últimos 10 anos de todas as ações do IBOVESPA
    e salva em um arquivo CSV.
    """
    try:
        # Determinar o caminho base do projeto
        if os.path.exists('results'):
            base_path = ''
        else:
            base_path = '..'
        
        # Usar o arquivo mais recente do IBrX-50
        data_atual = datetime.now().strftime('%d-%m-%y')
        nome_arquivo = os.path.join(base_path, 'results', f'IBXLDia_{data_atual}.csv')
        
        # Lê o arquivo CSV com as ações do IBRX50
        df_acoes = pd.read_csv(nome_arquivo, skiprows=1)
        df_acoes.columns = ['Código']
        tickers = df_acoes['Código'].tolist()
        
        # Data inicial (10 anos atrás)
        data_inicial = (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')
        
        # Lista para armazenar todos os dados históricos
        dados_historicos = []
        
        print("Iniciando download do histórico das ações...")
        
        # Processa cada ação
        for ticker in tickers:
            ticker_yf = f"{ticker}.SA"
            try:
                # Obtém dados históricos da ação
                acao = yf.Ticker(ticker_yf)
                hist = acao.history(start=data_inicial)
                
                if hist.empty:
                    continue
                
                # Adiciona informações ao histórico
                hist['Ticker'] = ticker
                hist['Nome'] = ticker  # Como não temos o nome da empresa no novo arquivo, usamos o próprio ticker
                
                # Reseta o índice para transformar a data em coluna
                hist = hist.reset_index()
                hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
                
                # Adiciona aos dados históricos
                dados_historicos.append(hist)
                
                print(f"Dados baixados para {ticker}")
                
                # Pausa para evitar sobrecarga na API
                time.sleep(1)
                
            except Exception as e:
                print(f"Erro ao baixar dados de {ticker}: {str(e)}")
                continue
        
        # Combina todos os dados históricos
        if dados_historicos:
            df_historico = pd.concat(dados_historicos, ignore_index=True)
            
            # Seleciona e renomeia as colunas relevantes
            df_historico = df_historico[['Date', 'Ticker', 'Nome', 'Close', 'Volume']]
            df_historico.columns = ['Data', 'Simbolo', 'Nome_Empresa', 'Preco', 'Volume']
            
            # Calcula a variação diária
            df_historico['Variacao'] = df_historico.groupby('Simbolo')['Preco'].pct_change() * 100
            
            # Determinar o caminho base do projeto
            if os.path.exists('results'):
                base_path = ''
            else:
                base_path = '..'
            
            # Salva o histórico em CSV
            nome_arquivo = os.path.join(base_path, 'results', 'historico_acoes.csv')
            df_historico.to_csv(nome_arquivo, index=False)
            print("\nHistórico salvo com sucesso em 'historico_acoes.csv'")
            
            return df_historico
        else:
            print("\nNenhum dado histórico foi baixado")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Erro ao processar dados históricos: {str(e)}")
        return pd.DataFrame()

def obter_melhores_e_piores_acoes(periodo='1d'):
    """
    Obtém as 5 melhores e 5 piores ações do período especificado usando o arquivo histórico.
    
    Args:
        periodo (str): Período de análise ('1d' para 30 dias, '1mo' para mensal, '1y' para anual)
    """
    try:
        # Lê o arquivo CSV com o histórico
        # Determinar o caminho base do projeto
        if os.path.exists('results'):
            base_path = ''
        else:
            base_path = '..'
        
        nome_arquivo = os.path.join(base_path, 'results', 'historico_acoes.csv')
        df_historico = pd.read_csv(nome_arquivo)
        df_historico['Data'] = pd.to_datetime(df_historico['Data'])
        
        # Obtém a data mais recente
        data_mais_recente = df_historico['Data'].max()
        
        # Filtra e agrega dados conforme o período
        if periodo == '1d':
            # Últimos 30 dias
            data_inicio = data_mais_recente - pd.Timedelta(days=30)
            df_periodo = df_historico[df_historico['Data'] >= data_inicio].copy()
            # Calcular variação no período
            df_periodo = df_periodo.groupby('Simbolo').agg({
                'Preco': ['first', 'last'],
                'Nome_Empresa': 'first'
            }).reset_index()
            df_periodo.columns = ['Simbolo', 'Preco_Inicial', 'Preco_Final', 'Nome_Empresa']
            df_periodo['Variacao'] = ((df_periodo['Preco_Final'] / df_periodo['Preco_Inicial']) - 1) * 100
            
        elif periodo == '1mo':
            # Agregar por mês
            df_historico['Mes_Ano'] = df_historico['Data'].dt.to_period('M')
            df_periodo = df_historico.groupby(['Simbolo', 'Mes_Ano', 'Nome_Empresa'])['Preco'].mean().reset_index()
            df_periodo = df_periodo.sort_values(['Simbolo', 'Mes_Ano'])
            # Calcular variação do último mês
            df_periodo = df_periodo.groupby('Simbolo').agg({
                'Preco': ['first', 'last'],
                'Nome_Empresa': 'first'
            }).reset_index()
            df_periodo.columns = ['Simbolo', 'Preco_Inicial', 'Preco_Final', 'Nome_Empresa']
            df_periodo['Variacao'] = ((df_periodo['Preco_Final'] / df_periodo['Preco_Inicial']) - 1) * 100
            
        else:  # '1y'
            # Agregar por ano
            df_historico['Ano'] = df_historico['Data'].dt.year
            df_periodo = df_historico.groupby(['Simbolo', 'Ano', 'Nome_Empresa'])['Preco'].mean().reset_index()
            df_periodo = df_periodo.sort_values(['Simbolo', 'Ano'])
            # Calcular variação do último ano
            df_periodo = df_periodo.groupby('Simbolo').agg({
                'Preco': ['first', 'last'],
                'Nome_Empresa': 'first'
            }).reset_index()
            df_periodo.columns = ['Simbolo', 'Preco_Inicial', 'Preco_Final', 'Nome_Empresa']
            df_periodo['Variacao'] = ((df_periodo['Preco_Final'] / df_periodo['Preco_Inicial']) - 1) * 100
        
        if df_periodo.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # Formata os dados para exibição
        df_periodo['Preço'] = df_periodo['Preco_Final'].round(2)
        df_periodo['Variação (%)'] = df_periodo['Variacao'].round(2)
        df_periodo['Símbolo'] = df_periodo['Simbolo']
        df_periodo['Empresa'] = df_periodo['Nome_Empresa']
        
        # Ordena por variação e seleciona as 5 melhores e piores
        melhores = df_periodo.nlargest(5, 'Variacao')[['Símbolo', 'Empresa', 'Preço', 'Variação (%)']]
        piores = df_periodo.nsmallest(5, 'Variacao')[['Símbolo', 'Empresa', 'Preço', 'Variação (%)']]
        
        return melhores, piores
    
    except Exception as e:
        print(f"Erro ao processar dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()


def get_current_prices_acoes(df):
    """
    Obtém os preços atuais das ações e calcula a variação percentual em relação ao preço de compra.
    
    Args:
        df (DataFrame): DataFrame contendo as informações das ações com as colunas:
                        id_acoes, nome, preco_inicial, etc.
    
    Returns:
        DataFrame: DataFrame atualizado com os preços atuais e variação percentual.
    """
    try:
        # Criar uma cópia do DataFrame para evitar SettingWithCopyWarning
        df_acoes = df.copy(deep=True)
        
        # Mapear os símbolos das ações
        symbol_map = {
            "PETR4": "PETR4.SA",
            "VALE3": "VALE3.SA",
            "ITUB4": "ITUB4.SA", 
            "MGLU3": "MGLU3.SA",
            "WEGE3": "WEGE3.SA",
            # Adicione mais mapeamentos conforme necessário
        }
        
        # Calcular o preço atual em BRL e a variação percentual
        df_acoes.loc[:, "preco_atual_br"] = df_acoes["nome"].apply(
            lambda x: yf.Ticker(symbol_map.get(x, f"{x}.SA")).history(period="1d")["Close"].iloc[-1]
            if x in symbol_map or x.endswith(".SA") else 0.0
        )
        
        # Renomear preco_inicial para manter consistência com outras tabelas
        df_acoes.loc[:, "preco_compra_br"] = df_acoes["preco_inicial"]
        
        # Calcular a variação percentual
        df_acoes.loc[:, "variacao_percentual_br"] = (
            (df_acoes["preco_atual_br"] - df_acoes["preco_compra_br"]) / df_acoes["preco_compra_br"] * 100
        ).round(2)
        
        # Calcular o valor investido
        df_acoes.loc[:, "valor_investido_br"] = df_acoes["quantidade"] * df_acoes["preco_compra_br"]
        
        return df_acoes
        
    except Exception as e:
        print(f"Erro ao obter preços atuais das ações: {str(e)}")
        # Retornar o DataFrame original em caso de erro
        return df

