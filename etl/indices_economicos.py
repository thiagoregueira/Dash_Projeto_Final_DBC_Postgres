from bcb import sgs
from datetime import datetime, timedelta
import pandas as pd

def buscar_dados_economicos():
    # Calculando a data inicial (10 anos atrás)
    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=365*10)
    
    # Códigos das séries temporais do BCB
    codigos = {
        'SELIC': 432,      # Taxa Selic
        'IPCA': 433,       # IPCA - Índice nacional de preços ao consumidor-amplo
        'IGP-M': 189,      # IGP-M - Índice geral de preços do mercado
        'INPC': 188,       # INPC - Índice nacional de preços ao consumidor
        'CDI': 12,         # Taxa CDI
        'PIB_MENSAL': 4380 # PIB Mensal - Valores correntes (em R$ milhões)
    }
    
    # Dicionário para armazenar os DataFrames
    dados = {}
    
    # Buscando dados para cada indicador
    for nome, codigo in codigos.items():
        try:
            df = sgs.get(codigo, start=data_inicial, end=data_final)
            df = pd.DataFrame(df)
            df.columns = [nome]
            dados[nome] = df
        except Exception as e:
            print(f"Erro ao buscar dados do {nome}: {str(e)}")
    
    # Concatenando todos os DataFrames
    df_final = pd.concat(dados.values(), axis=1)
    
    # Salvando os dados em CSV
    df_final.to_csv('results/dados_economicos.csv')
    
    return df_final

if __name__ == "__main__":
    buscar_dados_economicos()