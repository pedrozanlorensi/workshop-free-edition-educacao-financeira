# Databricks notebook source
# DBTITLE 1,Preparar dados: juntar fundos com indicadores macro
from pyspark.sql.functions import col, year, month, avg, count, round as spark_round

# Carregar tabelas
df_rendimentos = spark.table("workspace.default.rendimento_mensal_fundos")
df_indicadores = spark.table("workspace.default.indicadores_macro")

# Preparar indicadores para join (extrair ano e mês)
df_indicadores_prep = df_indicadores \
    .withColumn("ano", year("mes_referencia")) \
    .withColumn("mes", month("mes_referencia")) \
    .select("ano", "mes", "inflacao_mensal_pct", "cdi_mensal_pct", "selic_anualizada_fim_mes_pct")

# Join dos rendimentos com indicadores
df_analise = df_rendimentos \
    .join(df_indicadores_prep, ["ano", "mes"], "inner") \
    .filter(col("rendimento_mensal_pct").isNotNull())

print(f"Dataset integrado criado com {df_analise.count()} registros")
print(f"Período: {df_analise.agg({'ano': 'min'}).collect()[0][0]} a {df_analise.agg({'ano': 'max'}).collect()[0][0]}")
display(df_analise.limit(5))

# COMMAND ----------

# DBTITLE 1,Análise 1: Correlação entre fundos e indicadores por tipo
from pyspark.sql.functions import corr, sum as spark_sum, row_number

# Calcular correlações entre rendimento dos fundos e indicadores macro
df_correlacao = df_analise.groupBy("tipo_fundo").agg(
    spark_round(corr("rendimento_mensal_pct", "inflacao_mensal_pct"), 4).alias("corr_inflacao"),
    spark_round(corr("rendimento_mensal_pct", "cdi_mensal_pct"), 4).alias("corr_cdi"),
    spark_round(corr("rendimento_mensal_pct", "selic_anualizada_fim_mes_pct"), 4).alias("corr_selic"),
    count("*").alias("n_observacoes")
).orderBy(col("corr_cdi").desc())

print("\n=== MATRIZ DE CORRELAÇÃO: FUNDOS vs INDICADORES MACRO ===")
print("Correlação de Pearson entre rendimento mensal e indicadores\n")
display(df_correlacao)

# COMMAND ----------

# DBTITLE 1,Mapa de Correlação (Heatmap)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Converter para pandas e preparar matriz de correlação
df_corr_pd = df_correlacao.toPandas()

# Criar matriz de correlação no formato adequado
corr_matrix = df_corr_pd[['corr_inflacao', 'corr_cdi', 'corr_selic']].values
tipos = df_corr_pd['tipo_fundo'].values
indicadores = ['Inflação', 'CDI', 'SELIC']

# Criar figura
fig, ax = plt.subplots(figsize=(10, 6))

# Criar heatmap
im = ax.imshow(corr_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)

# Configurar eixos
ax.set_xticks(np.arange(len(indicadores)))
ax.set_yticks(np.arange(len(tipos)))
ax.set_xticklabels(indicadores, fontsize=11)
ax.set_yticklabels([t.replace('_', ' ').title() for t in tipos], fontsize=11)

# Rotacionar labels do eixo x
plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

# Adicionar valores nas células
for i in range(len(tipos)):
    for j in range(len(indicadores)):
        valor = corr_matrix[i, j]
        cor_texto = 'white' if abs(valor) > 0.5 else 'black'
        text = ax.text(j, i, f'{valor:.4f}',
                      ha="center", va="center", color=cor_texto,
                      fontsize=12, fontweight='bold')

# Adicionar colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Correlação de Pearson', rotation=270, labelpad=20, fontsize=11, fontweight='bold')

# Título
ax.set_title('Mapa de Correlação: Rendimento dos Fundos vs Indicadores Macroeconômicos\n(Correlação de Pearson)',
             fontsize=14, fontweight='bold', pad=20)

# Labels dos eixos
ax.set_xlabel('Indicadores Macroeconômicos', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Tipo de Fundo', fontsize=12, fontweight='bold', labelpad=10)

# Ajustar layout
plt.tight_layout()

# Adicionar texto explicativo
fig.text(0.5, 0.02, 
         'Valores próximos de +1 indicam forte correlação positiva | Valores próximos de -1 indicam forte correlação negativa | Valores próximos de 0 indicam correlação fraca',
         ha='center', fontsize=9, style='italic', wrap=True)

plt.subplots_adjust(bottom=0.12)
display(plt.show())

# COMMAND ----------

# DBTITLE 1,Análise 2: Performance acumulada - Fundos vs Inflação vs CDI
# Comparar quantos fundos bateram a inflação e o CDI
df_performance = df_analise.groupBy("nome_fundo", "gestora", "tipo_fundo").agg(
    count("*").alias("meses_analisados"),
    spark_round(avg("rendimento_mensal_pct"), 4).alias("rend_medio_mensal_pct"),
    spark_round(avg("inflacao_mensal_pct"), 4).alias("inflacao_media_mensal_pct"),
    spark_round(avg("cdi_mensal_pct"), 4).alias("cdi_medio_mensal_pct"),
    spark_round(avg(col("rendimento_mensal_pct") - col("inflacao_mensal_pct")), 4).alias("excesso_vs_inflacao_pct"),
    spark_round(avg(col("rendimento_mensal_pct") - col("cdi_mensal_pct")), 4).alias("excesso_vs_cdi_pct")
)

# Classificar fundos
df_performance = df_performance \
    .withColumn("bateu_inflacao", col("excesso_vs_inflacao_pct") > 0) \
    .withColumn("bateu_cdi", col("excesso_vs_cdi_pct") > 0)

# Estatísticas gerais
print("\n=== PERFORMANCE DOS FUNDOS vs BENCHMARKS ===")
print(f"Total de fundos analisados: {df_performance.count()}\n")

df_resumo = df_performance.groupBy("tipo_fundo").agg(
    count("*").alias("total_fundos"),
    spark_sum(col("bateu_inflacao").cast("int")).alias("bateram_inflacao"),
    spark_sum(col("bateu_cdi").cast("int")).alias("bateram_cdi")
).withColumn("pct_bateu_inflacao", spark_round(col("bateram_inflacao") / col("total_fundos") * 100, 2)) \
 .withColumn("pct_bateu_cdi", spark_round(col("bateram_cdi") / col("total_fundos") * 100, 2))

print("Resumo por tipo de fundo:")
display(df_resumo)

print("\nTop 10 fundos com melhor excesso sobre CDI:")
display(df_performance.orderBy(col("excesso_vs_cdi_pct").desc()).limit(10))

# COMMAND ----------

# DBTITLE 1,Gráfico: Performance dos Fundos vs Benchmarks
import matplotlib.pyplot as plt

# Converter para pandas
df_resumo_pd = df_resumo.toPandas().sort_values('pct_bateu_cdi', ascending=True)

# Criar figura com dois subplots lado a lado
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Gráfico 1: Percentual de fundos que bateram benchmarks
tipos = df_resumo_pd['tipo_fundo'].values
x = np.arange(len(tipos))
width = 0.35

rects1 = ax1.barh(x - width/2, df_resumo_pd['pct_bateu_inflacao'], width, label='Bateram Inflação', color='#6C5CE7')
rects2 = ax1.barh(x + width/2, df_resumo_pd['pct_bateu_cdi'], width, label='Bateram CDI', color='#00B894')

ax1.set_xlabel('Percentual de Fundos (%)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Tipo de Fundo', fontsize=12, fontweight='bold')
ax1.set_title('% de Fundos que Superaram os Benchmarks\n(Rendimento médio mensal)', fontsize=13, fontweight='bold')
ax1.set_yticks(x)
ax1.set_yticklabels(tipos)
ax1.legend(loc='lower right', fontsize=10)
ax1.set_xlim(0, 105)
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# Adicionar valores nas barras
for rect in rects1 + rects2:
    width_val = rect.get_width()
    ax1.annotate(f'{width_val:.0f}%',
                xy=(width_val, rect.get_y() + rect.get_height() / 2),
                xytext=(3, 0),
                textcoords="offset points",
                ha='left', va='center',
                fontsize=10, fontweight='bold')

# Gráfico 2: Top 10 fundos com melhor excesso sobre CDI
df_top10_pd = df_performance.orderBy(col("excesso_vs_cdi_pct").desc()).limit(10).toPandas()

# Colorir por tipo de fundo
colors_map = {'renda variavel': '#E74C3C', 'multimercado': '#3498DB', 'renda fixa': '#2ECC71'}
colors = [colors_map[tipo] for tipo in df_top10_pd['tipo_fundo']]

ax2.barh(range(len(df_top10_pd)), df_top10_pd['excesso_vs_cdi_pct'], color=colors)
ax2.set_xlabel('Excesso sobre CDI (% mensal)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Fundo', fontsize=12, fontweight='bold')
ax2.set_title('Top 10 Fundos - Maior Retorno Acima do CDI\n(Rendimento médio mensal)', fontsize=13, fontweight='bold')
ax2.set_yticks(range(len(df_top10_pd)))
ax2.set_yticklabels([f"{nome[:30]}..." if len(nome) > 30 else nome for nome in df_top10_pd['nome_fundo']], fontsize=9)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3, linestyle='--')

# Adicionar valores nas barras
for i, v in enumerate(df_top10_pd['excesso_vs_cdi_pct']):
    ax2.text(v + 0.02, i, f'+{v:.2f}%', va='center', fontsize=9, fontweight='bold')

# Adicionar legenda de cores no segundo gráfico
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=colors_map['renda variavel'], label='Renda Variável'),
                   Patch(facecolor=colors_map['multimercado'], label='Multimercado'),
                   Patch(facecolor=colors_map['renda fixa'], label='Renda Fixa')]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=9)

plt.tight_layout()
display(plt.show())

# COMMAND ----------

# DBTITLE 1,Análise 3: Padrões de sazonalidade (por mês do ano)
# Análise de sazonalidade: rendimento médio por mês do ano
df_sazonalidade = df_analise.groupBy("mes", "tipo_fundo").agg(
    spark_round(avg("rendimento_mensal_pct"), 4).alias("rend_medio_pct"),
    spark_round(avg("inflacao_mensal_pct"), 4).alias("inflacao_media_pct"),
    spark_round(avg("cdi_mensal_pct"), 4).alias("cdi_medio_pct"),
    count("*").alias("n_observacoes")
).orderBy("tipo_fundo", "mes")

print("\n=== ANÁLISE DE SAZONALIDADE ===")
print("Rendimento médio por mês do ano (agregando todos os anos)\n")
display(df_sazonalidade)

# Identificar melhor e pior mês para cada tipo de fundo
from pyspark.sql import Window

window_tipo = Window.partitionBy("tipo_fundo").orderBy(col("rend_medio_pct").desc())
df_sazonalidade_rank = df_sazonalidade \
    .withColumn("rank", row_number().over(window_tipo))

print("\nMelhor mês para cada tipo de fundo:")
display(df_sazonalidade_rank.filter(col("rank") == 1).select("tipo_fundo", "mes", "rend_medio_pct"))

window_tipo_asc = Window.partitionBy("tipo_fundo").orderBy(col("rend_medio_pct").asc())
df_sazonalidade_rank_pior = df_sazonalidade \
    .withColumn("rank", row_number().over(window_tipo_asc))

print("\nPior mês para cada tipo de fundo:")
display(df_sazonalidade_rank_pior.filter(col("rank") == 1).select("tipo_fundo", "mes", "rend_medio_pct"))# COMMAND ----------

# DBTITLE 1,Gráfico: Padrões de Sazonalidade
import matplotlib.pyplot as plt

# Converter para pandas e preparar dados
df_saz_pd = df_sazonalidade.toPandas()

# Criar figura com subplot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Gráfico 1: Rendimento médio por mês (linhas por tipo de fundo)
meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

for tipo in df_saz_pd['tipo_fundo'].unique():
    df_tipo = df_saz_pd[df_saz_pd['tipo_fundo'] == tipo].sort_values('mes')
    
    if tipo == 'renda variavel':
        ax1.plot(df_tipo['mes'], df_tipo['rend_medio_pct'], marker='o', linewidth=2.5, 
                label=tipo.title(), color='#E74C3C', markersize=8)
    elif tipo == 'multimercado':
        ax1.plot(df_tipo['mes'], df_tipo['rend_medio_pct'], marker='s', linewidth=2.5, 
                label=tipo.title(), color='#3498DB', markersize=8)
    else:
        ax1.plot(df_tipo['mes'], df_tipo['rend_medio_pct'], marker='^', linewidth=2.5, 
                label=tipo.title(), color='#2ECC71', markersize=8)

ax1.set_xlabel('Mês', fontsize=12, fontweight='bold')
ax1.set_ylabel('Rendimento Médio Mensal (%)', fontsize=12, fontweight='bold')
ax1.set_title('Sazonalidade dos Rendimentos por Tipo de Fundo\n(Rendimento médio mensal por mês do ano, agregando 2000-2026)', 
              fontsize=14, fontweight='bold', pad=20)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(meses_nomes)
ax1.legend(loc='best', fontsize=11, framealpha=0.9)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_ylim(0, max(df_saz_pd['rend_medio_pct']) * 1.15)

# Adicionar linha horizontal para CDI médio
cdi_medio_geral = df_saz_pd['cdi_medio_pct'].mean()
ax1.axhline(y=cdi_medio_geral, color='orange', linestyle='--', linewidth=2, 
            label=f'CDI Médio ({cdi_medio_geral:.2f}%)', alpha=0.7)

# Gráfico 2: Comparação entre melhor e pior mês
melhor_mes_pd = df_sazonalidade_rank.filter(col("rank") == 1).toPandas()
pior_mes_pd = df_sazonalidade_rank_pior.filter(col("rank") == 1).toPandas()

tipos_ordem = ['renda fixa', 'multimercado', 'renda variavel']
x = np.arange(len(tipos_ordem))
width = 0.35

# Ordenar dataframes
melhor_mes_pd = melhor_mes_pd.set_index('tipo_fundo').loc[tipos_ordem].reset_index()
pior_mes_pd = pior_mes_pd.set_index('tipo_fundo').loc[tipos_ordem].reset_index()

rects1 = ax2.bar(x - width/2, melhor_mes_pd['rend_medio_pct'], width, 
                 label='Melhor Mês', color='#27AE60', alpha=0.8)
rects2 = ax2.bar(x + width/2, pior_mes_pd['rend_medio_pct'], width, 
                 label='Pior Mês', color='#E67E22', alpha=0.8)

ax2.set_xlabel('Tipo de Fundo', fontsize=12, fontweight='bold')
ax2.set_ylabel('Rendimento Médio (%)', fontsize=12, fontweight='bold')
ax2.set_title('Amplitude Sazonal: Melhor vs Pior Mês por Tipo de Fundo', 
              fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels([t.replace('_', ' ').title() for t in tipos_ordem])
ax2.legend(loc='upper right', fontsize=11)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Adicionar valores e meses nas barras
for i, rect in enumerate(rects1):
    height = rect.get_height()
    mes_nome = meses_nomes[int(melhor_mes_pd.iloc[i]['mes']) - 1]
    ax2.annotate(f'{height:.2f}%\n({mes_nome})',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=9, fontweight='bold')

for i, rect in enumerate(rects2):
    height = rect.get_height()
    mes_nome = meses_nomes[int(pior_mes_pd.iloc[i]['mes']) - 1]
    ax2.annotate(f'{height:.2f}%\n({mes_nome})',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=9, fontweight='bold')

plt.tight_layout()
display(plt.show())

