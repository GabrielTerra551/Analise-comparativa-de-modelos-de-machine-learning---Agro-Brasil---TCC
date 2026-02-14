# Regressao Linear via Rede Neural - SLCE3 (Dataset Janelas)

Este modelo segue o mesmo padrao visual e de relatorios usado no notebook de regressao linear.

## Decisoes e configuracoes
- Dataset: datasets_janelas/regressao/SLCE3_tratado.csv
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
- metricas_slce3_janelas.csv
- serie_temporal_slce3_janelas.png
- residuos_slce3_janelas.png
- real_vs_predito_slce3_janelas.png
- comparacao_metricas_slce3_janelas.png
- histograma_residuos_slce3_janelas.png
- residuos_temporais_slce3_janelas.png
- dispersao_ic_slce3_janelas.png
- evolucao_metricas_slce3_janelas.png

## Observacoes
- A normalizacao e aplicada via StandardScaler antes do MLP.
