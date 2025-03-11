import os
import logging
from datetime import datetime
from etl.scraping_ibrx50 import download_ibrx50_data as baixar_dados_ibrx50
from etl.tratar_ibrx50 import processar_ibrx50 as tratar_dados_ibrx50
from etl.acoes import baixar_historico_acoes
from etl.criptomoedas import baixar_historico_cripto
from etl.cambio import baixar_historico_cambio
from etl.indices_economicos import buscar_dados_economicos

# Criar diretório results se não existir
if not os.path.exists('results'):
    os.makedirs('results')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/etl_process.log'),
        logging.StreamHandler()
    ]
)

def main():
    """
    Função principal que orquestra o processo de ETL dos dados financeiros.
    A ordem de execução é importante devido às dependências entre os processos.
    """
    try:
        # Verificar se o diretório results foi criado
        if os.path.exists('results'):
            logging.info("Diretório 'results' existe e está pronto para uso")
        start_time = datetime.now()
        logging.info("Iniciando processo de ETL")

        # 1. Download e tratamento dos dados do IBrX-50
        # logging.info("1. Iniciando download dos dados do IBrX-50")
        # baixar_dados_ibrx50()
        # logging.info("2. Iniciando tratamento dos dados do IBrX-50")
        # tratar_dados_ibrx50()

        # 2. Download do histórico das ações
        logging.info("3. Iniciando download do histórico das ações")
        baixar_historico_acoes()

        # 3. Download do histórico das criptomoedas
        logging.info("4. Iniciando download do histórico das criptomoedas")
        baixar_historico_cripto()

        # 4. Download do histórico do câmbio
        logging.info("5. Iniciando download do histórico do câmbio")
        baixar_historico_cambio()

        # 5. Download dos índices econômicos
        logging.info("6. Iniciando download dos índices econômicos")
        buscar_dados_economicos()

        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"Processo de ETL concluído com sucesso! Duração total: {duration}")

    except Exception as e:
        logging.error(f"Erro durante o processo de ETL: {str(e)}")
        raise

if __name__ == "__main__":
    main()
