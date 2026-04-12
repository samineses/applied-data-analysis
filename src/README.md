#o que é feito no código

1.Você estima o intervalo de amostragem do sinal
-é o tempo típico entre amostras e a escala temporal real do sinal.
2.calculo da janela
-O valor da janela controla o quanto o sinal é suavizado
-O valor da janela depende diretamente de três fatores: 
-da frequência de amostragem (ex:1 amostra a cada 0,5 s)
	- da capacidade motora do paciente:
		janelas curtas demais → deixam ruído passar
		janelas longas demais → achatam o movimento real
	-do tipo de movimento analisado:
		dorsiflexão voluntária → janela maior
		tremor / espasticidade → janela menor
		marcha lenta → janela intermediária
-O calculo é feito:
-pré‑processamento auxiliar ( base_smooth_window=3) é o tamanho da janela da suavização mínima inicial.
-restrição fisiológica mínima (min_window=5) é o limite inferior permitido para a janela final, evita janelas muito pequenas que não filtram ruído adequadamente e geram falsos extremos
-restrição fisiológica máxima (max_window=6)  é o limite superior permitido para a janela final. Evita suavização excessiva que achata picos e introduz perda de informação funcional


3.Aplica‑se uma média móvel centrada (rolling = janela deslizante):

-Cada ponto passa a representar a média dos pontos ao redor(pontos vizinhos) e a largura da vizinhança é o valor da janela calculada automáticamente. O sinal é suavizado sem deslocamento temporal (centrer=true).

-Cada valor suavizado representa o comportamento médio do movimento ao longo de (Janela*0,5) segundos
	-escala temporal da suavização ≈ W⋅dt

-média móvel é um filtro passa‑baixa:
-Isso reduz oscilações de alta frequência associadas ao ruído de rastreamento (ruído de frame-a-frame) ou seja Remove ruído e oscilações rápidas do software
-Também preserva a dinâmica global do movimento, preserva componentes de baixa frequência (movimento funcional),  ou seja Mantém apenas a tendência real do movimento.
-Amplitude_suave: versão filtrada da amplitude original, onde pequenas oscilações rápidas são removidas, que remove: ruído do software, erros frame‑a‑frame, micro‑oscilações irreais. E preserva tendência geral do movimento, ciclos lentos e contínuos, alcance funcional real.
-Nesse novo sinal suavizado: extremos são calculados após o filtro, elimina flutuações de curto prazo. Ele também é mais contínuo, biomecanicamente plausível e representa melhor o movimento funcional.

#visualização
gráfico de tendência:
Como o movimento evolui ao longo da sessão?
(fadiga, ganho, estabilidade, perda de amplitude)


gráfico de distribuição (boxplot)
Qual é o padrão global do movimento?
(amplitude típica, variabilidade, eventos raros)


resumo: “Inicialmente, aplicou‑se um filtro de média móvel centrada para suavizar o sinal de amplitude articular. Em seguida, os máximos e mínimos foram recalculados a partir do sinal suavizado, considerando apenas variações superiores ao desvio‑padrão e respeitando limitações temporais do movimento do paciente.”



#O desvio padrão é útil para filtragem local; a agregação por blocos já cumpre esse papel de forma mais robusta para sinais longos.

Analisar máximos e mínimos do sinal suavizado (ponto a ponto)
O que isso responde:
“Onde estão os picos?”
“Qual foi o maior valor absoluto?”
Limitações:
ainda gera muitos eventos em sinais longos
continua sensível a:
ciclos muito frequentes
variações rápidas
não escala bem para sessões longas
👉 Bom para:
sinais curtos
análise detalhada de ciclos individuais

🔹 Analisar comportamento por blocos (o que você faz agora)
O que isso responde:
“Qual foi o padrão típico do movimento?”
“Como a amplitude evolui ao longo da sessão?”
“Há fadiga, ganho ou perda funcional?”
Vantagens:
reduz milhares de amostras a poucas dezenas
elimina ruído pontual
escala para:
sessões longas
múltiplas articulações
vários dias
👉 Muito mais alinhado com a pergunta clínica:
“Qual foi a amplitude máxima típica?


#Opniao final da IA:
clinicamente, as perguntas relevantes costumam ser:

Qual foi a amplitude máxima típica?
Houve redução ou aumento ao longo da sessão?
O movimento ficou mais irregular com o tempo?
Existem outliers claros (erros de tracking)?

e a resposta não exige ver cada ponto do sinal

Você precisa ver:

como o padrão muda ao longo do tempo.
Para marcha longa, a pergunta clínica correta é outra:

“Como o movimento evolui ao longo da sessão?”


Para dados longos de marcha, você prefere ver:
-Como a amplitude média e máxima evoluem ao longo da sessão (curvas lentas)
-Distribuição do movimento por blocos (boxplots)
-Ambos (tendência + distribuição)

Ao migrar de uma análise de eventos individuais para uma análise agregada por blocos de tempo, você trocou sensibilidade local por robustez funcional — o que é exatamente o comportamento desejado para sinais longos e aplicações clínicas.




#Abaixo são coisas usadas em versoes anteriores do código:
-Impõe um intervalo mínimo de tempo:
	pois Dois extremos não podem ocorrer muito próximos no tempo
	resultado:
		máximos reais → maior amplitude funcional atingida
		mínimos reais → menor amplitude funcional
		sem falsos picos consecutivos
#tempo_min: segundos mínimos entre extremos:
	-Impede que dois extremos (máximo ou mínimo) sejam detectados muito próximos no tempo.
	-depois de detectar um extremo, o código ignora qualquer outro extremo até passar tempo_min segundos.
	-tempo_min representa o tempo fisiológico mínimo que o paciente precisa para:
		inverter o movimento
		mudar de tendência
		executar parte significativa de um ciclo motor
	Regra prática:tempo_min deve ser menor que a duração do movimento, mas maior que o ruído do sistema.



#tempo_min controla o quão rápido um novo extremo pode aparecer
#tempo_min definido como 2s:
	o sinal já está sendo suavizado em uma escala de 2,5 s
	não faz sentido aceitar extremos em intervalos menores que isso
	garante que:
		cada extremo detectado representa um evento distinto
		não é apenas flutuação dentro da mesma janela de suavização

#tempo_min representa o tempo fisiológico mínimo necessário para o paciente alterar a direção do movimento articular.
	não é um parâmetro matemático, é um parâmetro biomecânico.

#O tempo_min deve ser derivado da janela (tempo_min ≈ (janela × intervalo_amostragem) × fator)

-Usa o desvio‑padrão como critério: representa a variabilidade do ruído, Um extremo só é aceito se a variação local for maior que o desvio‑padrão
	Isso garante que:
		pequenas oscilações → ignoradas
		grandes variações → movimento real

