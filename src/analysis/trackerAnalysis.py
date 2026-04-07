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

    # Conversões
    df["tempo"] = pd.to_numeric(df["tempo"], errors="coerce")
    df["Amplitudes"] = (
        df["Amplitudes"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
    df["Amplitudes"] = pd.to_numeric(df["Amplitudes"], errors="coerce")
    df = df.dropna().reset_index(drop=True)

    # Salva SOMENTE os dados base
    df.to_excel(arquivo_saida, index=False)

# ===============================
# Parâmetros temporais
# ===============================
dt = df["tempo"].diff().median()

# ===============================
# Estimativa automática da janela
# ===============================
janela, info = estimate_optimal_window(df, dt)

print(f"Janela estimada automaticamente: {janela}")
#print("Detalhes da estimativa:", info)

# ===============================
# 1) Suavização
# ===============================
df["Amplitude_suave"] = df["Amplitudes"].rolling(
    window=janela, center=True
).mean()

df_suave = df.dropna().reset_index(drop=True)

# ===============================
# 2) Desvio padrão
# ===============================
sigma = df_suave["Amplitude_suave"].std()
tempo_min = janela * dt

# ===============================
# 3) Máximos e mínimos reais
# ===============================
extremos = []
ultimo_tempo = -np.inf

for i in range(1, len(df_suave) - 1):
    y_prev = df_suave.loc[i-1, "Amplitude_suave"]
    y = df_suave.loc[i, "Amplitude_suave"]
    y_next = df_suave.loc[i+1, "Amplitude_suave"]
    t = df_suave.loc[i, "tempo"]

    if y_prev < y > y_next:
        if abs(y - (y_prev + y_next) / 2) > sigma and t - ultimo_tempo >= tempo_min:
            extremos.append([t, y, "máximo"])
            ultimo_tempo = t

    if y_prev > y < y_next:
        if abs(y - (y_prev + y_next) / 2) > sigma and t - ultimo_tempo >= tempo_min:
            extremos.append([t, y, "mínimo"])
            ultimo_tempo = t

extremos_df = pd.DataFrame(
    extremos, columns=["tempo", "Amplitude_suave", "tipo"]
)

# ===============================
# CONFIG: tamanho fixo da figura
# ===============================
W_PX, H_PX = 3840, 1942
DPI = 100
FIGSIZE = (W_PX / DPI, H_PX / DPI)

arquivo_img = os.path.join(
    pasta_origem,
    f"{os.path.splitext(os.path.basename(arquivo_origem))[0]}_AMPL_{W_PX}x{H_PX}.png"
)

# ===============================
# Gráfico
# ===============================
plt.figure(figsize=FIGSIZE, dpi=DPI)

plt.plot(df["tempo"], df["Amplitudes"],
         color="blue", alpha=0.3, label="Amplitudes")

plt.plot(df_suave["tempo"], df_suave["Amplitude_suave"],
         color="red", linewidth=2, label="Amplitude suavizada")

plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.title(
    f"Janela automática = {janela} | "
    f"tempo_min = {tempo_min:.2f} s | "
    f"dt = {dt:.2f} s"
)
plt.grid(True)
plt.legend()

plt.savefig(arquivo_img, dpi=DPI, bbox_inches=None, pad_inches=0)
plt.show()

print(f"Arquivo base utilizado:\n{arquivo_saida}")
print(f"Imagem salva em:\n{arquivo_img}")