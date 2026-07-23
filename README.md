# 📊 Projeto: Análise de Fundos de Investimento

Análise de performance de fundos de investimento comparados com indicadores macroeconômicos (CDI, SELIC e inflação), construída no Databricks Free Edition para o workshop de educação financeira.

> Os dados são **fictícios** e gerados sinteticamente. Nomes de gestoras e fundos não correspondem a instituições reais.

## 🗄️ Tabelas Unity Catalog

| Tabela | Conteúdo | Registros |
|---|---|---|
| `workspace.default.quotas_fundos` | Cotas diárias de fechamento por fundo | 520.125 |
| `workspace.default.indicadores_macro` | Indicadores macro mensais (inflação, CDI, SELIC) | 319 |
| `workspace.default.rendimento_mensal_fundos` | Rendimento mensal calculado por fundo | 23.925 |
| `workspace.default.indicadores_macro_acumulados` | CDI e inflação acumulados | 319 |

## 📁 Estrutura do Projeto

Os notebooks ficam na pasta `0_PraticaFreeEdition` do workspace e rodam em sequência.

### 1️⃣ Carga de Dados (`1_CargaArquivos`)
- Lê os CSVs do volume `/Volumes/workspace/default/arquivos/` e grava as tabelas Unity Catalog.
- `quotas_fundos.csv` → `workspace.default.quotas_fundos`
- `indicadores_macro.csv` → `workspace.default.indicadores_macro`

### 2️⃣ Rendimento Mensal (`2_RendimentoMensalFundos`)
- Calcula o rendimento mensal percentual de cada fundo.
- Fórmula: `((valor_fim_mes / valor_mes_anterior) - 1) * 100`
- Saída: `workspace.default.rendimento_mensal_fundos`

### 3️⃣ Análise Estatística (`3_AnaliseFundosVsIndices`)
- Correlações entre fundos e indicadores (CDI, inflação).
- Performance vs benchmarks e sazonalidade por mês.
- Visualizações com matplotlib/seaborn.

### 4️⃣ Cálculo de Acumulados (`4_IndicadoresMacroAcumulados`)
- Rendimento composto acumulado do CDI e inflação acumulada.
- Fórmula: `(produto de (1 + retorno_mensal)) - 1`
- Saída: `workspace.default.indicadores_macro_acumulados`

### 5️⃣ Dashboard Interativo
- 5 filtros locais: Tipo de Fundo, Gestora, Ano, Mês, Fundo.
- 4 KPIs: Total de Fundos, Rendimento Médio, % que Bateu o CDI, % que Bateu a Inflação.
- 5 visualizações: Evolução Temporal, Ranking, Performance por Tipo, Fundos por Gestora, Sazonalidade.

## 💡 Insights Principais

### Performance vs Benchmarks
- **Renda Fixa:** correlação praticamente perfeita com o CDI (~1,00); ~72% dos meses batem o CDI.
- **Multimercado:** correlação parcial com o CDI (~0,13, parcela pós-fixada + book de risco); ~54% batem o CDI.
- **Renda Variável:** independente do CDI (~0,00), maior volatilidade; ~49% batem o CDI.

### Sazonalidade
- Padrões sazonais leves, que variam por tipo de fundo.

### Gestoras
- 15 gestoras fictícias, cada uma com múltiplos fundos de diferentes tipos.

## 🚀 Como Usar

1. **Atualizar dados:** substitua os CSVs no volume e execute os notebooks `1 → 2 → 4`. O dashboard reflete as tabelas automaticamente.
2. **Análise exploratória:** use o notebook `3` para análises ad-hoc.
3. **Dashboard:** use os filtros para recortes específicos e selecione fundos individuais para comparação.

## 🧪 Geração dos Dados Fictícios

Os CSVs são sintéticos. Pontos de modelagem que os deixam plausíveis:
- **SELIC anualizada** varia em regime, com passos pequenos de 0,25–0,50 p.p. e ciclos de vários meses.
- **CDI mensal** derivado da SELIC (um pouco abaixo da meta, convertido para base mensal).
- **Inflação mensal** em torno de ~5% a.a., com sazonalidade leve e ruído.
- **Fundos de renda fixa** acompanham o CDI diário (spread e tracking error mínimos), resultando em correlação ~1,00 com o CDI.
