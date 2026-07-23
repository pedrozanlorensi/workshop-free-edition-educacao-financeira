# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Título
# MAGIC %md
# MAGIC # Indicadores Macroeconômicos Acumulados

# COMMAND ----------

# DBTITLE 1,Descrição
# MAGIC %md
# MAGIC Este notebook calcula os rendimentos acumulados (compostos) do CDI e da Inflação mês a mês, partindo dos dados mensais armazenados em `workspace.default.indicadores_macro`.
# MAGIC
# MAGIC O cálculo de rendimento composto acumulado usa a fórmula: `(produto de (1 + retorno_mensal)) - 1`
# MAGIC
# MAGIC A tabela resultante `workspace.default.indicadores_macro_acumulados` será utilizada no dashboard de análise de fundos.

# COMMAND ----------

# DBTITLE 1,Carregar dados originais
# MAGIC %sql
# MAGIC SELECT * FROM workspace.default.indicadores_macro ORDER BY mes_referencia

# COMMAND ----------

# DBTITLE 1,Calcular indicadores acumulados
import pandas as pd

# Carregar dados da query SQL anterior
df = spark.sql("SELECT * FROM workspace.default.indicadores_macro ORDER BY mes_referencia").toPandas()

# Calcular CDI acumulado (rendimento composto)
df['cdi_acumulado_pct'] = ((1 + df['cdi_mensal_pct'] / 100).cumprod() - 1) * 100

# Calcular Inflação acumulada (rendimento composto)
df['inflacao_acumulada_pct'] = ((1 + df['inflacao_mensal_pct'] / 100).cumprod() - 1) * 100

# Selecionar colunas finais
df_final = df[['mes_referencia', 'data_fim_mes', 'cdi_mensal_pct', 'cdi_acumulado_pct', 'inflacao_mensal_pct', 'inflacao_acumulada_pct', 'selic_anualizada_fim_mes_pct']]

print(f"Total de registros processados: {len(df_final)}")

# COMMAND ----------

# DBTITLE 1,Visualizar amostra dos últimos 12 meses
# Exibir últimos 12 meses
display(df_final.tail(12))

# COMMAND ----------

# DBTITLE 1,Salvar tabela no Unity Catalog
# Converter para Spark DataFrame e salvar como tabela
spark.createDataFrame(df_final).write.mode("overwrite").saveAsTable("workspace.default.indicadores_macro_acumulados")

print("✅ Tabela workspace.default.indicadores_macro_acumulados criada com sucesso!")

# COMMAND ----------

# DBTITLE 1,Conclusão
# MAGIC %md
# MAGIC ## ✅ Tabela criada com sucesso!
# MAGIC
# MAGIC A tabela `workspace.default.indicadores_macro_acumulados` foi criada contendo os indicadores macroeconômicos com valores mensais e acumulados.

# COMMAND ----------

