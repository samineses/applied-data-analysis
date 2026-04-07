import pandas as pd
from tkinter import Tk, filedialog
import os

# Selecionar arquivo
Tk().withdraw()
arquivo = filedialog.askopenfilename(
    title="Selecione o arquivo .xlsx",
    filetypes=[("Excel files", "*.xlsx")]
)

# Ler Excel
df = pd.read_excel(arquivo)

# Preservar 1ª e 2ª colunas
df_simples = df.iloc[:, [0, 1]].copy()

# Criar coluna tempo a partir do Frame
df_simples.insert(
    0,
    "tempo",
    df_simples.iloc[:, 0] * 0.5
)

# Remover coluna Frame
df_simples = df_simples.drop(df_simples.columns[1], axis=1)

# Salvar novo arquivo
saida = os.path.splitext(arquivo)[0] + "_SIMPLIFICADO.xlsx"
df_simples.to_excel(saida, index=False)

print(f"Arquivo gerado:\n{saida}")