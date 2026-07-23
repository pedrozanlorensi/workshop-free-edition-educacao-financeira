# 📊 Projeto: Análise de Fundos de Investimento

Análise de performance de fundos de investimento comparados com indicadores macroeconômicos (CDI, SELIC e inflação), construída no **Databricks Free Edition** para o workshop de educação financeira.

> Os dados são **fictícios** e gerados sinteticamente. Nomes de gestoras e fundos não correspondem a instituições reais.

## 🤖 Desenvolvido com Assistência de IA

Este projeto foi construído do começo ao fim com forte apoio de **assistentes de IA**, e essa é uma parte central da proposta do workshop: mostrar como IA acelera o ciclo de dados e análise no Databricks.

A IA foi usada em praticamente todas as etapas:

- **Geração de dados sintéticos** — os scripts em `scripts/` foram escritos com IA para produzir séries plausíveis: SELIC em regime com cortes graduais, CDI derivado da SELIC, inflação em torno da meta e fundos de renda fixa atrelados ao CDI. A IA também ajudou a *validar* a modelagem (por exemplo, medindo a correlação renda fixa × CDI e corrigindo o gerador quando ela não fazia sentido).
- **Escrita dos notebooks** — transformações em PySpark, cálculo de rendimentos, acumulados e as visualizações em matplotlib/seaborn foram desenvolvidas com o **Databricks Assistant** e outros assistentes de código.
- **Depuração** — a IA diagnosticou um problema de ordem de execução no notebook de análise (células que usavam DataFrames definidos mais adiante) e reordenou o notebook para rodar de ponta a ponta.
- **Dashboard** — a estrutura de datasets, KPIs e filtros do dashboard AI/BI foi desenhada com apoio de IA.
- **Documentação** — este README e a documentação do projeto foram redigidos com IA.

> **Dica para o workshop:** experimente reproduzir cada etapa pedindo ao Databricks Assistant. O objetivo não é copiar o código pronto, e sim praticar o diálogo com a IA — descrever a intenção, revisar o que ela sugere e validar os resultados.

## 📁 Estrutura do Repositório

```
.
├── README.md
├── notebooks/                      # notebooks do projeto (Databricks / PySpark)
│   ├── 0_DocumentacaoProjeto.py
│   ├── 1_CargaArquivos.py
│   ├── 2_RendimentoMensalFundos.py
│   ├── 3_AnaliseFundosVsIndices.py
│   └── 4_IndicadoresMacroAcumulados.py
├── dados/                          # dados fictícios em CSV
│   ├── quotas_fundos.csv           # cotas diárias por fundo (2000–2026)
│   └── indicadores_macro.csv       # inflação, CDI e SELIC mensais
├── dashboard/                      # definição do dashboard AI/BI
│   └── Analise de Fundos de Investimento.lvdash.json
└── scripts/                        # geradores dos dados sintéticos
    ├── gerar_macro.py              # gera dados/indicadores_macro.csv
    └── gerar_fundos.py             # gera dados/quotas_fundos.csv (usa o macro)
```

## 🗄️ Tabelas Unity Catalog

| Tabela | Conteúdo | Registros |
|---|---|---|
| `workspace.default.quotas_fundos` | Cotas diárias de fechamento por fundo | 520.125 |
| `workspace.default.indicadores_macro` | Indicadores macro mensais (inflação, CDI, SELIC) | 319 |
| `workspace.default.rendimento_mensal_fundos` | Rendimento mensal calculado por fundo | 23.925 |
| `workspace.default.indicadores_macro_acumulados` | CDI e inflação acumulados | 319 |

## 🔄 Fluxo dos Notebooks

Ordem de execução: **1 → 2 → 4 → 3**.

### 1️⃣ Carga de Dados (`1_CargaArquivos`)
- Lê os CSVs do volume `/Volumes/workspace/default/arquivos/` e grava as tabelas Unity Catalog.
- `quotas_fundos.csv` → `workspace.default.quotas_fundos`
- `indicadores_macro.csv` → `workspace.default.indicadores_macro`

### 2️⃣ Rendimento Mensal (`2_RendimentoMensalFundos`)
- Calcula o rendimento mensal percentual de cada fundo.
- Fórmula: `((valor_fim_mes / valor_mes_anterior) - 1) * 100`
- Saída: `workspace.default.rendimento_mensal_fundos`

### 4️⃣ Cálculo de Acumulados (`4_IndicadoresMacroAcumulados`)
- Rendimento composto acumulado do CDI e inflação acumulada.
- Fórmula: `(produto de (1 + retorno_mensal)) - 1`
- Saída: `workspace.default.indicadores_macro_acumulados`

### 3️⃣ Análise Estatística (`3_AnaliseFundosVsIndices`)
- Correlações entre fundos e indicadores (CDI, inflação, SELIC).
- Performance vs benchmarks e sazonalidade por mês.
- Visualizações com matplotlib/seaborn.

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

### No Databricks
1. Importe os notebooks de `notebooks/` para o seu workspace.
2. Suba os CSVs de `dados/` para um volume (ex.: `/Volumes/workspace/default/arquivos/`).
3. Execute os notebooks na ordem **1 → 2 → 4 → 3** (ou `Run all` em cada um).
4. Importe `dashboard/Analise de Fundos de Investimento.lvdash.json` como dashboard AI/BI. Ele lê as tabelas ao vivo e reflete os dados automaticamente.

### Regenerar os dados fictícios
```bash
pip install numpy pandas
python scripts/gerar_macro.py     # gera dados/indicadores_macro.csv
python scripts/gerar_fundos.py    # gera dados/quotas_fundos.csv (depende do macro)
```

## 🧪 Modelagem dos Dados Fictícios

Os CSVs são sintéticos. Pontos de modelagem que os deixam plausíveis:
- **SELIC anualizada** varia em regime, com passos pequenos de 0,25–0,50 p.p. e ciclos de vários meses.
- **CDI mensal** derivado da SELIC (um pouco abaixo da meta, convertido para base mensal).
- **Inflação mensal** em torno de ~5% a.a., com sazonalidade leve e ruído.
- **Fundos de renda fixa** acompanham o CDI diário (spread e tracking error mínimos), resultando em correlação ~1,00 com o CDI.
- **Multimercado** combinam parcela pós-fixada (CDI) com um book de risco e alfa.
- **Renda variável** seguem risco de mercado, independentes do CDI.
