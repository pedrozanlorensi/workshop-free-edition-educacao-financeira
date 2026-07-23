# Databricks notebook source
# DBTITLE 1,Calcular rendimento mensal dos fundos
from pyspark.sql import Window
from pyspark.sql.functions import col, year, month, last, lag, round as spark_round

# Ler dados de quotas
df_quotas = spark.table("workspace.default.quotas_fundos")

# Para cada fundo e mês, pegar o último valor de quota do mês
df_ultimo_valor_mes = df_quotas \
    .groupBy(
        col("nome_fundo"),
        col("gestora"),
        col("tipo_fundo"),
        year("data").alias("ano"),
        month("data").alias("mes")
    ) \
    .agg(last("valor_quota_fechamento", ignorenulls=True).alias("valor_quota_fim_mes"))

# Criar janela particionada por fundo, ordenada por ano/mês
window_spec = Window.partitionBy("nome_fundo").orderBy("ano", "mes")

# Calcular rendimento mensal: (valor_atual / valor_anterior - 1) * 100
df_rendimento_mensal = df_ultimo_valor_mes \
    .withColumn("valor_quota_mes_anterior", lag("valor_quota_fim_mes").over(window_spec)) \
    .withColumn(
        "rendimento_mensal_pct",
        spark_round(
            ((col("valor_quota_fim_mes") / col("valor_quota_mes_anterior")) - 1) * 100,
            4
        )
    ) \
    .select(
        "nome_fundo",
        "gestora",
        "tipo_fundo",
        "ano",
        "mes",
        "valor_quota_fim_mes",
        "valor_quota_mes_anterior",
        "rendimento_mensal_pct"
    ) \
    .orderBy("nome_fundo", "ano", "mes")

# Salvar como tabela
df_rendimento_mensal.write.mode("overwrite").saveAsTable("workspace.default.rendimento_mensal_fundos")

print(f"Tabela workspace.default.rendimento_mensal_fundos criada com {df_rendimento_mensal.count()} registros")
display(df_rendimento_mensal.filter(col("rendimento_mensal_pct").isNotNull()).limit(10))

# COMMAND ----------

# DBTITLE 1,Estatísticas dos rendimentos mensais
# Estatísticas gerais dos rendimentos mensais
df_stats = spark.sql("""
SELECT 
    tipo_fundo,
    COUNT(DISTINCT nome_fundo) as qtd_fundos,
    ROUND(AVG(rendimento_mensal_pct), 4) as rendimento_medio_pct,
    ROUND(MIN(rendimento_mensal_pct), 4) as rendimento_minimo_pct,
    ROUND(MAX(rendimento_mensal_pct), 4) as rendimento_maximo_pct,
    ROUND(STDDEV(rendimento_mensal_pct), 4) as desvio_padrao_pct
FROM workspace.default.rendimento_mensal_fundos
WHERE rendimento_mensal_pct IS NOT NULL
GROUP BY tipo_fundo
ORDER BY rendimento_medio_pct DESC
""")

print("Estatísticas de rendimento mensal por tipo de fundo:")
display(df_stats)