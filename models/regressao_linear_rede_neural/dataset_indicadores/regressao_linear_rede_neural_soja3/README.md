# Regressao Linear via Rede Neural - SOJA3 (Dataset Indicadores)

Este modelo segue o mesmo padrao visual e de relatorios usado no notebook de regressao linear.

## Decisoes e configuracoes
- Dataset: datasets_indicadores/regressao/SOJA3_tratado.csv
- Features: Close, Low, High, Open
- Targets: Close_3d_fut, Close_7d_fut, Close_15d_fut, Close_30d_fut
- Split: 80/20 com random_state=42
- Modelo: MLPRegressor com Pipeline (StandardScaler + MLP)
- Metricas: R2, MAE, RMSE

## Parametros do MLPRegressor
- hidden_layer_sizes: (64, 32)
- activation: relu
- solver: adam
- alpha: 0.0001
- learning_rate_init: 0.001
- max_iter: 1000
- random_state: 42

## Saidas geradas
- metricas_soja3_indicadores.csv
- serie_temporal_soja3_indicadores.png
- residuos_soja3_indicadores.png
- real_vs_predito_soja3_indicadores.png
- comparacao_metricas_soja3_indicadores.png
- histograma_residuos_soja3_indicadores.png
- residuos_temporais_soja3_indicadores.png
- dispersao_ic_soja3_indicadores.png
- evolucao_metricas_soja3_indicadores.png

## Observacoes
- A normalizacao e aplicada via StandardScaler antes do MLP.
