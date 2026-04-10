import pandas as pd
import os
import numpy as np
from tkinter import Tk, filedialog
import matplotlib.pyplot as plt
from windowEstimation import estimate_optimal_window

# ===============================
# Seleção do arquivo
# ===============================
Tk().withdraw()
arquivo_origem = filedialog.askopenfilename(
    title="Selecione o arquivo .xlsx",
    filetypes=[("Excel files", "*.xlsx")]
)

pasta_origem = os.path.dirname(arquivo_origem)
base_nome = os.path.splitext(os.path.basename(arquivo_origem))[0]

arquivo_auditoria = os.path.join(
    pasta_origem,
    f"{base_nome}_AUDITORIA.xlsx"
)

arquivo_blocos = os.path.join(
    pasta_origem,
    f"{base_nome}_BLOCOS30S.xlsx"
)

# ===============================
# Leitura e padronização
# ===============================
df = pd.read_excel(
    arquivo_origem,
    usecols=[0, 1],
    names=["tempo", "Amplitudes"],
    header=0
)

df["tempo"] = pd.to_numeric(df["tempo"], errors="coerce")
df["Amplitudes"] = (
    df["Amplitudes"].astype(str).str.replace(",", ".", regex=False)
)
df["Amplitudes"] = pd.to_numeric(df["Amplitudes"], errors="coerce")
df = df.dropna().reset_index(drop=True)

# ===============================
# Parâmetros temporais
# ===============================
dt = df["tempo"].diff().median()

# ===============================
# Estimativa automática da janela
# ===============================
janela, _ = estimate_optimal_window(df, dt)
print(f"Janela estimada automaticamente: {janela}")

# ===============================
# Suavização
# ===============================
df["Amplitude_suave"] = df["Amplitudes"].rolling(
    window=janela, center=True
).mean()

df_suave = df.dropna().reset_index(drop=True)

# ===============================
# SALVAR TABELA DE AUDITORIA
# ===============================
df_suave.to_excel(arquivo_auditoria, index=False)
print(f"Tabela de auditoria salva em: {arquivo_auditoria}")

# ===============================
# RESUMO POR BLOCOS DE 30s
# ===============================
BLOCO_TEMPO = 30.0

df_suave["bloco"] = (df_suave["tempo"] // BLOCO_TEMPO).astype(int)

resumo_blocos = (
    df_suave
    .groupby("bloco")["Amplitude_suave"]
    .agg(
        max_medio="max",
        min_medio="min",
        media="mean"
    )
    .reset_index()
)

resumo_blocos["tempo_bloco"] = resumo_blocos["bloco"] * BLOCO_TEMPO
resumo_blocos["amplitude_funcional"] = (
    resumo_blocos["max_medio"] - resumo_blocos["min_medio"]
)

resumo_blocos = resumo_blocos[
    ["tempo_bloco", "max_medio", "min_medio", "amplitude_funcional"]
]

# ===============================
# SALVAR TABELA DE BLOCOS
# ===============================
resumo_blocos.to_excel(arquivo_blocos, index=False)
print(f"Tabela por blocos salva em: {arquivo_blocos}")

# ===============================
# VISUALIZAÇÃO — OPÇÃO C
# ===============================

# ----- Gráfico de tendência -----
plt.figure(figsize=(16, 5))

plt.plot(resumo_blocos["tempo_bloco"], resumo_blocos["max_medio"],
         label="Amplitude máxima", linewidth=2)

plt.plot(resumo_blocos["tempo_bloco"], resumo_blocos["min_medio"],
         label="Amplitude mínima", linewidth=2)

plt.plot(resumo_blocos["tempo_bloco"], resumo_blocos["amplitude_funcional"],
         label="Amplitude funcional", linewidth=2.5, linestyle="--")

plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.title(
    f"Tendência do movimento | Janela = {janela} | Blocos de {BLOCO_TEMPO:.0f}s"
)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ----- Gráfico de distribuição -----
plt.figure(figsize=(10, 5))

plt.boxplot(
    df_suave["Amplitude_suave"],
    vert=True,
    patch_artist=True,
    boxprops=dict(facecolor="lightgray")
)

plt.ylabel("Amplitude")
plt.title("Distribuição global da amplitude do movimento")
plt.grid(axis="y")
plt.tight_layout()
plt.show()

print("Processamento concluído com sucesso.")
