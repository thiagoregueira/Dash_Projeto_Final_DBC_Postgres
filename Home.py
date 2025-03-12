import streamlit as st
import pandas as pd
from datetime import datetime
from style.style_config import apply_custom_style, add_footer

# Configuração global da página
st.set_page_config(
    page_title="FinUp",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Dashboard financeiro desenvolvido com Streamlit"},
)

# Aplicar estilo customizado
apply_custom_style()

# Título principal com destaque
st.title(" Bem-vindo ao FinUp Investimentos - Seu Dashboard Financeiro Completo")

# Introdução ao dashboard
st.markdown("""
## O que é o FinUp Investimentos?

O FinUp Investimentos é um dashboard financeiro interativo que fornece informações atualizadas sobre diversos aspectos do mercado financeiro brasileiro e internacional. Nossa plataforma foi desenvolvida para ajudar tanto investidores experientes quanto iniciantes a acompanhar os principais indicadores e ativos financeiros de forma simples e intuitiva.

### O que você encontrará nestes dashboards:

1. **Ações Brasileiras (IBRX50)** 
   * Acompanhe o desempenho das principais ações da bolsa brasileira
   * Visualize gráficos de evolução de preços
   * Identifique as melhores e piores performances do mercado

2. **Criptomoedas** 
   * Monitore as principais criptomoedas do mercado global
   * Acompanhe as cotações em dólar americano (USD)
   * Analise tendências e variações de preço

3. **Câmbio** 
   * Verifique as cotações das principais moedas em relação ao Real (BRL)
   * Acompanhe a variação cambial ao longo do tempo
   * Compare o desempenho entre diferentes moedas

4. **Indicadores Econômicos** 
   * Consulte os principais indicadores da economia brasileira
   * Visualize previsões futuras baseadas em análise de dados
   * Entenda como os indicadores se relacionam entre si
""")

# Explicação detalhada de cada seção
st.markdown("""
## Detalhes de cada seção

### Ações Brasileiras
Na seção de **Ações Brasileiras**, você pode:
* Selecionar qualquer ação do índice IBRX50 (que reúne as 50 ações mais negociadas da B3)
* Escolher diferentes períodos de análise: 30 dias, mensal ou anual
* Visualizar a evolução do preço da ação em um gráfico interativo
* Consultar informações como preço atual, máximo e mínimo no período
* Ver um ranking das 5 melhores e 5 piores ações em termos de desempenho

Esta ferramenta é ideal para quem quer acompanhar o mercado acionário brasileiro e identificar oportunidades de investimento.

### Criptomoedas
Na seção de **Criptomoedas**, você encontra:
* Uma lista das principais criptomoedas do mercado (Bitcoin, Ethereum, etc.)
* Gráficos de evolução de preço em dólares americanos (USD)
* Opções para analisar diferentes períodos: 30 dias, mensal ou anual
* Informações sobre preço atual, máximo e mínimo
* Ranking das criptomoedas com melhor e pior desempenho no período selecionado

Esta seção é perfeita para quem deseja acompanhar o mercado de criptoativos e suas flutuações.

### Câmbio
Na seção de **Câmbio**, você pode:
* Selecionar diferentes moedas internacionais e ver sua cotação em relação ao Real (BRL)
* Visualizar a evolução da taxa de câmbio em diferentes períodos
* Comparar o desempenho de várias moedas simultaneamente
* Identificar tendências de valorização ou desvalorização

Esta ferramenta é essencial para quem precisa acompanhar o mercado de câmbio, seja para viagens, importações/exportações ou investimentos internacionais.

### Indicadores Econômicos
Na seção de **Indicadores Econômicos**, você tem acesso a:
* Dados atualizados dos principais indicadores da economia brasileira:
  * **SELIC**: Taxa básica de juros da economia
  * **IPCA**: Índice oficial de inflação do Brasil
  * **IGP-M**: Índice usado para reajustes de contratos de aluguel
  * **INPC**: Índice que mede a inflação para famílias de baixa renda
  * **CDI**: Taxa de referência para investimentos de renda fixa
  * **PIB Mensal**: Indicador da atividade econômica do país
* Gráficos de evolução histórica de cada indicador
* Comparativo entre diferentes indicadores
* Previsões futuras baseadas em modelos estatísticos

Esta seção é fundamental para entender o cenário macroeconômico brasileiro e suas possíveis tendências.
""")

# Adicionando dicas de uso
st.markdown("""
## Como usar o dashboard

1. **Navegação**: Use o menu lateral para alternar entre as diferentes seções do dashboard.

2. **Interatividade**: Todos os gráficos são interativos. Você pode:
   * Passar o mouse sobre os pontos para ver valores específicos
   * Clicar e arrastar para dar zoom em áreas específicas
   * Clicar nos itens da legenda para mostrar/ocultar séries
   * Baixar o gráfico como imagem usando os botões no canto superior direito

3. **Filtros**: Em cada seção, você encontrará opções para:
   * Selecionar ativos específicos (ações, criptomoedas, moedas)
   * Escolher diferentes períodos de análise
   * Personalizar a visualização dos dados

4. **Atualização**: Os dados são atualizados regularmente para fornecer as informações mais recentes do mercado.
""")

# Adicionando informações sobre a última atualização
st.sidebar.markdown(
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
)

# Adicionando um bloco de informações adicionais
st.markdown("""
## Informações importantes

### Fontes de dados
* **Ações**: Dados obtidos da B3 (Bolsa de Valores do Brasil)
* **Criptomoedas**: Dados obtidos de exchanges internacionais
* **Câmbio**: Cotações fornecidas pelo Banco Central do Brasil
* **Indicadores**: Dados do IBGE, Banco Central e outras instituições oficiais

### Limitações
* Os dados apresentados possuem caráter informativo e não constituem recomendação de investimento
* Pode haver um pequeno atraso na atualização de algumas informações
* As previsões de indicadores são baseadas em modelos estatísticos e estão sujeitas a margens de erro

### Dúvidas frequentes
* **Os dados são em tempo real?** A maioria dos dados é atualizada diariamente, não em tempo real
* **Posso usar esses dados para tomar decisões de investimento?** Os dados são informativos e devem ser complementados com outras análises
* **Como são feitas as previsões de indicadores?** Utilizamos modelos de regressão linear com base nos dados históricos
""")

# Adicionar footer padronizado
add_footer()
