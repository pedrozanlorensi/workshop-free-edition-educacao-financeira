import os

import numpy as np
import pandas as pd

# Caminhos relativos a raiz do repo (scripts/ fica um nivel abaixo)
BASE = os.path.join(os.path.dirname(__file__), "..", "dados")

rng = np.random.default_rng(42)

# Dias uteis de 2000-01-01 ate 2026-07-31
datas = pd.bdate_range("2000-01-03", "2026-07-31")
n_dias = len(datas)

# --- CDI mensal (do arquivo macro) convertido em retorno diario por dia util ---
# Requer que scripts/gerar_macro.py tenha sido executado antes.
macro = pd.read_csv(os.path.join(BASE, "indicadores_macro.csv"))
macro["mes"] = pd.PeriodIndex(macro["mes_referencia"], freq="M")
cdi_por_mes = dict(zip(macro["mes"], macro["cdi_mensal_pct"] / 100.0))

dfd = pd.DataFrame({"data": datas})
dfd["mes"] = dfd["data"].dt.to_period("M")
dias_uteis_mes = dfd.groupby("mes")["data"].transform("count")
cdi_mensal_dia = dfd["mes"].map(cdi_por_mes).fillna(0.0).values
dias_uteis_mes = dias_uteis_mes.values
# retorno diario do CDI: (1+cdi_mensal)^(1/dias_uteis) - 1
cdi_diario = (1.0 + cdi_mensal_dia) ** (1.0 / dias_uteis_mes) - 1.0

# Nomes ficticios de gestoras (nao correspondem a instituicoes reais)
gestoras = [
    "Aurora Capital", "Boreal Asset", "Cerrado Investimentos", "Delta Prisma",
    "Equinocio Gestao", "Farol Capital", "Guara Investimentos", "Horizonte Asset",
    "Ignea Capital", "Jureia Investimentos", "Kaleido Gestao", "Lumen Capital",
    "Meridiano Asset", "Nimbus Investimentos", "Orion Prisma",
]

tipos = ["multimercado", "renda variavel", "renda fixa"]

# Temas ficticios para compor os nomes dos fundos
temas = ["Vertice", "Horizonte", "Pilar", "Cume", "Seleto",
         "Patrimonial", "Previdencia", "Consultoria", "Mais", "Essencial", "Liquidez",
         "Dinamico", "Estrategia", "Apice", "Rendimento"]

# Monta a lista de fundos (75 fundos garante > 500k linhas)
n_fundos = 75
fundos = []
for i in range(n_fundos):
    gestora = gestoras[i % len(gestoras)]
    tipo = tipos[i % len(tipos)]
    tema = temas[i % len(temas)]
    nome = f"{gestora.split()[0]} {tema} {i+1:02d} FI"
    fundos.append((nome, gestora, tipo))


def retorno_diario(tipo):
    if tipo == "renda fixa":
        # segue o CDI quase perfeitamente: pequeno spread + erro de tracking minimo
        spread_aa = rng.uniform(-0.003, 0.006)          # -0.3% a +0.6% a.a. vs CDI
        spread_dia = (1 + spread_aa) ** (1 / 252) - 1
        ruido = rng.normal(0, 0.00002, n_dias)          # tracking error diario minusculo
        return cdi_diario + spread_dia + ruido
    if tipo == "multimercado":
        # parcela pos-fixada (CDI) + componente de risco (busca CDI + alfa)
        alfa_aa = rng.uniform(0.01, 0.05)
        alfa_dia = (1 + alfa_aa) ** (1 / 252) - 1
        risco = rng.normal(0, 0.005, n_dias)            # vol de risco do book
        return cdi_diario + alfa_dia + risco
    # renda variavel: risco de mercado, independente do CDI
    mu = 0.00050
    return rng.normal(mu, 0.014, n_dias)


frames = []
for nome, gestora, tipo in fundos:
    ret = retorno_diario(tipo)
    cota = 100.0 * np.cumprod(1.0 + ret)
    frames.append(pd.DataFrame({
        "data": datas,
        "valor_quota_fechamento": np.round(cota, 6),
        "nome_fundo": nome,
        "gestora": gestora,
        "tipo_fundo": tipo,
    }))

df = pd.concat(frames, ignore_index=True)
df = df.sort_values(["data", "nome_fundo"]).reset_index(drop=True)

out = os.path.join(BASE, "quotas_fundos.csv")
df.to_csv(out, index=False, date_format="%Y-%m-%d")

print("linhas:", len(df))
print("fundos:", df["nome_fundo"].nunique())
print("periodo:", df["data"].min().date(), "a", df["data"].max().date())
print("tipos:", df["tipo_fundo"].value_counts().to_dict())
import os
print("tamanho MB:", round(os.path.getsize(out) / 1e6, 1))
