# Databricks notebook source
# DBTITLE 1,Título Principal
# MAGIC %md
# MAGIC # 📊 Projeto: Análise de Fundos de Investimento
# MAGIC
# MAGIC **Análise completa de performance de fundos de investimento brasileiros comparados com indicadores macroeconômicos (CDI e Inflação)**

# COMMAND ----------

# DBTITLE 1,Links Rápidos
# MAGIC %md
# MAGIC ## 🔗 Links Rápidos
# MAGIC
# MAGIC **Dashboard Principal:**
# MAGIC - [📈 Dashboard: Análise de Fundos de Investimento](/sql/dashboardsv3/01f186a26af51f08ab4a4bf4a4d67f5c)
# MAGIC
# MAGIC **Notebooks do Projeto:**
# MAGIC 1. [1_CargaDados](/editor/notebooks/602135652336778) - Carga inicial de dados (quotas_fundos.csv e indicadores_macro.csv)
# MAGIC 2. [2_RendimentoMensalFundos](/editor/notebooks/602135652336779) - Cálculo de rendimentos mensais dos fundos
# MAGIC 3. [3_AnaliseFundosVsIndices](/editor/notebooks/602135652336781) - Análises estatísticas e visualizações
# MAGIC 4. [4_IndicadoresMacroAcumulados](/editor/notebooks/3939804393705380) - Cálculo de indicadores acumulados (CDI e Inflação)

# COMMAND ----------

# DBTITLE 1,Tabelas Unity Catalog
# MAGIC %md
# MAGIC ## 🗄️ Tabelas Unity Catalog
# MAGIC
# MAGIC **Tabelas criadas pelo projeto:**
# MAGIC - `workspace.default.quotas_fundos` - Dados brutos de quotas de fundos
# MAGIC - `workspace.default.indicadores_macro` - Indicadores macroeconômicos mensais
# MAGIC - `workspace.default.rendimento_mensal_fundos` - Rendimentos mensais calculados (23,925 registros)
# MAGIC - `workspace.default.indicadores_macro_acumulados` - CDI e Inflação acumulados (319 registros)

# COMMAND ----------

# DBTITLE 1,Estrutura do Projeto
# MAGIC %md
# MAGIC ## 📁 Estrutura do Projeto
# MAGIC
# MAGIC ### 1️⃣ Carga de Dados (Notebook 1)
# MAGIC - Carrega arquivos CSV para tabelas Unity Catalog
# MAGIC - quotas_fundos.csv → workspace.default.quotas_fundos
# MAGIC - indicadores_macro.csv → workspace.default.indicadores_macro
# MAGIC
# MAGIC ### 2️⃣ Transformação (Notebook 2)
# MAGIC - Calcula rendimento mensal percentual de cada fundo
# MAGIC - Fórmula: ((valor_fim_mes / valor_mes_anterior) - 1) * 100
# MAGIC - Saída: workspace.default.rendimento_mensal_fundos
# MAGIC
# MAGIC ### 3️⃣ Análise Estatística (Notebook 3)
# MAGIC - Correlações entre fundos e indicadores (CDI, Inflação)
# MAGIC - Performance vs benchmarks
# MAGIC - Análise de sazonalidade por mês
# MAGIC - Visualizações com matplotlib/seaborn
# MAGIC
# MAGIC ### 4️⃣ Cálculo de Acumulados (Notebook 4)
# MAGIC - Rendimento composto acumulado do CDI
# MAGIC - Inflação acumulada
# MAGIC - Fórmula: (produto de (1 + retorno_mensal)) - 1
# MAGIC - Saída: workspace.default.indicadores_macro_acumulados
# MAGIC
# MAGIC ### 5️⃣ Dashboard Interativo
# MAGIC - 5 filtros locais: Tipo de Fundo, Gestora, Ano, Mês, Fundo
# MAGIC - 4 KPIs: Total Fundos, Rendimento Médio, % Bateu CDI, % Bateu Inflação
# MAGIC - 5 visualizações: Evolução Temporal, Ranking, Performance por Tipo, Fundos por Gestora, Sazonalidade

# COMMAND ----------

# DBTITLE 1,Insights Principais
# MAGIC %md
# MAGIC ## 💡 Insights Principais
# MAGIC
# MAGIC ### Performance vs Benchmarks
# MAGIC - **Renda Fixa:** Alta correlação com CDI (0.9979), 72% dos fundos batem CDI
# MAGIC - **Renda Variável:** Maior volatilidade, melhor performance em tendências de alta
# MAGIC - **Multimercado:** Performance intermediária com diversificação
# MAGIC
# MAGIC ### Sazonalidade
# MAGIC - **Março:** Melhor mês para renda variável
# MAGIC - **Dezembro:** Tradicionalmente forte para diversos tipos de fundos
# MAGIC - Padrões sazonais variam por tipo de fundo
# MAGIC
# MAGIC ### Gestoras
# MAGIC - Distribuição de fundos por gestora revela concentração no mercado
# MAGIC - Top gestoras gerenciam múltiplos fundos de diferentes tipos

# COMMAND ----------

# DBTITLE 1,Como Usar
# MAGIC %md
# MAGIC ## 🚀 Como Usar Este Projeto
# MAGIC
# MAGIC 1. **Atualizar Dados:**
# MAGIC    - Execute o Notebook 1 com novos arquivos CSV
# MAGIC    - Execute o Notebook 2 para recalcular rendimentos
# MAGIC    - Execute o Notebook 4 para atualizar acumulados
# MAGIC    - O dashboard será atualizado automaticamente
# MAGIC
# MAGIC 2. **Análise Exploratória:**
# MAGIC    - Use o Notebook 3 para análises estatísticas ad-hoc
# MAGIC    - Adicione novas células conforme necessário
# MAGIC
# MAGIC 3. **Dashboard Interativo:**
# MAGIC    - Acesse o dashboard via link acima
# MAGIC    - Use os filtros para análises específicas
# MAGIC    - Selecione fundos individuais para comparação detalhada
# MAGIC
# MAGIC 4. **Adicionar Novos Fundos:**
# MAGIC    - Adicione dados ao quotas_fundos.csv
# MAGIC    - Re-execute Notebooks 1 → 2 → 4
# MAGIC    - Dashboard refletirá automaticamente os novos dados