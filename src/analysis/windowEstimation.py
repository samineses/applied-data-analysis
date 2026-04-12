import numpy as np
import pandas as pd

# Função que que estima automaticamente a janela ideal de suavização baseada na dinâmica funcional do movimento.
#--------------------------------------------------------------------------------------------------------------
# Parâmetros:
# df : DataFrame - colunas ['tempo', 'Amplitudes']
# dt : float -Intervalo de amostragem (s)
# base_smooth_window : int - Suavização mínima para detectar picos (default=3)
# min_window : int - Limite inferior aceitável para janela
# max_window : int - Limite superior aceitável para janela
# ------------------------------------------------------------------------------
#

def estimate_optimal_window(df, dt, base_smooth_window=3, min_window=5, max_window=6):

    # [01] Suavização Mínima Incial(anti-ruído)
    # -------------------------------------------
    # Torna o sinal estável o suficiente para detectar picos e
    # ajusta a coluna de tempo para corresponder ao sinal suavizado y_base
    # --------------------------------------------------------------------------
    y_base = (df["Amplitudes"].rolling(window=base_smooth_window, center=True).mean().dropna().values)

    tempos_base = df.loc[df.index[base_smooth_window//2 : -base_smooth_window//2],"tempo"].values


    # [02] Detecção de picos funcionais
    # ----------------------------------
    # Percorre o sinal levemente suavizado (y_base) e identifica máximos locais​.
    # Verifica se há picos suficientes para estimar um período do movimento, o que 
    # funciona como um mecanismo de segurança, garantindo que o algoritmo não falhe 
    # nem produza estimativas incoerentes em sinais muito curtos ou pouco periódicos.
    #--------------------------------------------------------------------------------
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


    # [03] Período funcional típico do movimento
    #-------------------------------------
    # Calcula os intervalos de tempo entre picos consecutivos 
    # do movimento e estima o período funcional (periodo_medio).
    # Converte o periodo p/ numero de amostras
    # ----------------------------------------------------------
    intervalos = np.diff(picos_tempo)

    periodo_medio = np.median(intervalos) 

    janela_estimada = periodo_medio / dt
    janela_final = int(round(janela_estimada))

    
    # [04] Restringe a janela final a uma faixa fisiologicamente plausível
    # --------------------------------------------------------------------
    # evita janelas muito pequenas → subfiltragem e ruído
    # evita janelas muito grandes → superfiltragem e perda de dinâmica
    #------------------------------------------------------------------
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