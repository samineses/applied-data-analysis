import numpy as np
import pandas as pd

def estimate_optimal_window(df, dt,
                            base_smooth_window=3,
                            min_window=5,
                            max_window=6):
    """
    Estima automaticamente a janela ideal de suavização
    baseada na dinâmica funcional do movimento.

    Parâmetros
    ----------
    df : DataFrame
        Deve conter colunas ['tempo', 'Amplitudes']
    dt : float
        Intervalo de amostragem (s)
    base_smooth_window : int
        Suavização mínima para detectar picos (default=3)
    min_window : int
        Limite inferior aceitável para janela
    max_window : int
        Limite superior aceitável para janela

    Retorna
    -------
    janela_final : int
        Janela recomendada para análise
    info : dict
        Estatísticas auxiliares (período, intervalos, etc.)
    """

    # -------------------------------
    # 1) Suavização leve (anti-ruído)
    # -------------------------------
    y_base = (
        df["Amplitudes"]
        .rolling(window=base_smooth_window, center=True)
        .mean()
        .dropna()
        .values
    )

    tempos_base = df.loc[
        df.index[base_smooth_window//2 : -base_smooth_window//2],
        "tempo"
    ].values

    # -------------------------------
    # 2) Detecção de picos funcionais
    # -------------------------------
    picos_tempo = []

    for i in range(1, len(y_base) - 1):
        if y_base[i-1] < y_base[i] > y_base[i+1]:
            picos_tempo.append(tempos_base[i])

    picos_tempo = np.array(picos_tempo)

    if len(picos_tempo) < 2:
        # fallback seguro
        return min_window, {
            "motivo": "Poucos picos detectados",
            "periodo_estimado": None
        }

    # -------------------------------
    # 3) Período funcional do movimento
    # -------------------------------
    intervalos = np.diff(picos_tempo)

    periodo_medio = np.median(intervalos)

    # -------------------------------
    # 4) Converter período em janela
    # -------------------------------
    janela_estimada = periodo_medio / dt
    janela_final = int(round(janela_estimada))

    # Limitar a faixa fisiológica desejada
    janela_final = int(np.clip(
        janela_final, min_window, max_window
    ))

    info = {
        "periodo_medio_s": periodo_medio,
        "intervalos_s": intervalos,
        "janela_estimada_float": janela_estimada,
        "janela_final": janela_final
    }

    return janela_final, info