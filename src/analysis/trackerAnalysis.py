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
arquivo_saida = os.path.join(
    pasta_origem,
    f"{os.path.splitext(os.path.basename(arquivo_origem))[0]}_AMPL.xlsx"
)

# ===============================
# Carregamento dos dados (CACHE)
# ===============================
if os.path.exists(arquivo_saida):
    print("Arquivo _AMPL já existe. Lendo dados base...")
    df = pd.read_excel(arquivo_saida)
else:
    print("Criando arquivo _AMPL (cache de dados base)...")
    df = pd.read_excel(
        arquivo_origem,
        usecols=[0, 1],
        names=["tempo", "Amplitudes"],
        header=0
    )
    df["tempo"] = pd.to_numeric(df["tempo"], errors="coerce")
    df["Amplitudes"] = (
        df["Amplitudes"].astype(str)
        .str.replace(",", ".", regex=False)
    )
    df["Amplitudes"] = pd.to_numeric(df["Amplitudes"], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    df.to_excel(arquivo_saida, index=False)

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
# Suavização (ANÁLISE)
# ===============================
df["Amplitude_suave"] = df["Amplitudes"].rolling(
    window=janela, center=True
).mean()

# df_suave EXISTE A PARTIR DAQUI
df_suave = df.dropna().reset_index(drop=True)

# ===============================
# VARIABILIDADE (mantida para análise futura)
# ===============================
sigma = df_suave["Amplitude_suave"].std()
tempo_min = janela * dt

# =====================================================
# =============== VISUALIZAÇÃO — OPÇÃO C ===============
# =====================================================

# -------- CONFIGURAÇÕES --------
BLOCO_TEMPO = 30.0   # segundos por bloco (resumo temporal)
FIGSIZE_TREND = (16, 5)
FIGSIZE_DIST = (10, 5)

# ===============================
# 1) RESUMO TEMPORAL (TENDÊNCIA)
# ===============================

# Criar índice de blocos
df_suave["bloco"] = (df_suave["tempo"] // BLOCO_TEMPO).astype(int)

resumo = (
    df_suave
    .groupby("bloco")["Amplitude_suave"]
    .agg(
        max_medio="max",
        min_medio="min",
        media="mean"
    )
    .reset_index()
)

resumo["tempo_bloco"] = resumo["bloco"] * BLOCO_TEMPO
resumo["amplitude_funcional"] = resumo["max_medio"] - resumo["min_medio"]

# ----- Gráfico de tendência -----
plt.figure(figsize=FIGSIZE_TREND)

plt.plot(resumo["tempo_bloco"], resumo["max_medio"],
         label="Amplitude máxima", linewidth=2)

plt.plot(resumo["tempo_bloco"], resumo["min_medio"],
         label="Amplitude mínima", linewidth=2)

plt.plot(resumo["tempo_bloco"], resumo["amplitude_funcional"],
         label="Amplitude funcional (máx − mín)",
         linewidth=2.5, linestyle="--")

plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.title(
    f"Tendência do movimento | Janela = {janela} | Blocos de {BLOCO_TEMPO:.0f}s"
)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ===============================
# 2) DISTRIBUIÇÃO GLOBAL
# ===============================

plt.figure(figsize=FIGSIZE_DIST)

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

# ===============================
# FINALIZAÇÃO
# ===============================
print(f"Arquivo base utilizado: {arquivo_saida}")
print("Visualização concluída (Opção C).")
