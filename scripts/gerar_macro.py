import os

import numpy as np
import pandas as pd

# Caminhos relativos a raiz do repo (scripts/ fica um nivel abaixo)
BASE = os.path.join(os.path.dirname(__file__), "..", "dados")

rng = np.random.default_rng(7)

# Fim de cada mes, 2000-01 ate 2026-07
meses = pd.date_range("2000-01-31", "2026-07-31", freq="ME")
n = len(meses)

# --- SELIC anualizada (% a.a.) como caminho em regime ---
# Comeca em ~19%, faz movimentos lentos rumo a "targets" com passos de 0.25/0.50.
selic = np.empty(n)
nivel = 19.0
target = nivel
meses_no_target = 0
for i in range(n):
    if meses_no_target <= 0:
        # novo alvo do ciclo: entre 2% e 20%, mudanca tipica de -6 a +6 p.p.
        target = float(np.clip(nivel + rng.normal(0, 4.0), 2.0, 20.0))
        meses_no_target = int(rng.integers(6, 18))  # ciclo dura de 6 a 18 meses
    # aproxima do alvo com passos pequenos (0, 0.25 ou 0.50 p.p.)
    if nivel < target:
        passo = rng.choice([0.0, 0.25, 0.50], p=[0.35, 0.45, 0.20])
        nivel = min(nivel + passo, target)
    elif nivel > target:
        passo = rng.choice([0.0, 0.25, 0.50], p=[0.35, 0.45, 0.20])
        nivel = max(nivel - passo, target)
    meses_no_target -= 1
    selic[i] = round(nivel, 2)

# --- CDI mensal (%): segue a SELIC, um tiquinho abaixo, convertido pra base mensal ---
cdi_anual_efetiva = np.maximum(selic - 0.10, 0.5)  # CDI ~0.10 p.p. abaixo da meta
cdi_mensal = ((1 + cdi_anual_efetiva / 100) ** (1 / 12) - 1) * 100
cdi_mensal = np.round(cdi_mensal, 4)

# --- Inflacao mensal (%): media ~0.407%/mes (~5% a.a.), com sazonalidade e ruido ---
base_mensal = (1.05 ** (1 / 12) - 1) * 100  # ~0.4074%
mes_do_ano = meses.month.values
sazonal = 0.06 * np.sin(2 * np.pi * (mes_do_ano - 1) / 12)  # leve efeito sazonal
inflacao_mensal = base_mensal + sazonal + rng.normal(0, 0.18, n)
inflacao_mensal = np.round(inflacao_mensal, 4)

df = pd.DataFrame({
    "mes_referencia": meses.strftime("%Y-%m"),
    "data_fim_mes": meses.strftime("%Y-%m-%d"),
    "inflacao_mensal_pct": inflacao_mensal,
    "cdi_mensal_pct": cdi_mensal,
    "selic_anualizada_fim_mes_pct": selic,
})

out = os.path.join(BASE, "indicadores_macro.csv")
df.to_csv(out, index=False)

print("linhas:", len(df))
print("periodo:", df["mes_referencia"].iloc[0], "a", df["mes_referencia"].iloc[-1])
print("inflacao a.a. implicita media (%):", round(((1 + inflacao_mensal.mean()/100)**12 - 1)*100, 2))
print("SELIC min/max (%):", selic.min(), selic.max())
print(df.head(6).to_string(index=False))
print("...")
print(df.tail(4).to_string(index=False))
