## Visão geral do método

O sinal de amplitude articular é suavizado por uma média móvel centrada,
com janela adaptada ao tipo de movimento e à capacidade motora do paciente.
Após a suavização, a análise é feita de forma agregada por blocos de tempo,
priorizando robustez funcional em sinais longos.

### Pipeline
1. Estimativa do intervalo de amostragem
2. Cálculo automático da janela de suavização
3. Suavização por média móvel centrada
4. Extração de métricas agregadas por blocos
5. Visualização de tendência e distribuição


📄 A descrição metodológica detalhada e as decisões de projeto estão em  `docs/methodology.md`.

