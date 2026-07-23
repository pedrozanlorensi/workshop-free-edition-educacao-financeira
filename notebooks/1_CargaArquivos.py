# Databricks notebook source
# DBTITLE 1,Carregar indicadores_macro.csv
# Carregar arquivo indicadores_macro.csv para tabela
df_indicadores = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/Volumes/workspace/default/arquivos/indicadores_macro.csv")

# Salvar como tabela no workspace.default
df_indicadores.write.mode("overwrite").saveAsTable("workspace.default.indicadores_macro")

print(f"Tabela workspace.default.indicadores_macro criada com {df_indicadores.count()} registros")
display(df_indicadores.limit(5))

# COMMAND ----------

# DBTITLE 1,Carregar quotas_fundos.csv
# Carregar arquivo quotas_fundos.csv para tabela
df_quotas = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/Volumes/workspace/default/arquivos/quotas_fundos.csv")

# Salvar como tabela no workspace.default
df_quotas.write.mode("overwrite").saveAsTable("workspace.default.quotas_fundos")

print(f"Tabela workspace.default.quotas_fundos criada com {df_quotas.count()} registros")
display(df_quotas.limit(5))