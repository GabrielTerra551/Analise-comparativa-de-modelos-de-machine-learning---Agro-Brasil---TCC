# XGBoost - SLCE3 (Dataset Base)

Este modelo segue o mesmo padrao visual e de relatorios usado nos notebooks de classificacao existentes (ex.: regressao logistica).

## Decisoes e configuracoes
- Dataset: datasets_base/classificacao/SLCE3_tratado.csv
- Features: Close, Low, High, Open
- Targets: target_3d, target_7d, target_15d, target_30d (binario: 1 = Alta, 0 = Baixa/Estavel)
- Split: 80/20 com estratificacao e random_state=42
- Modelo: XGBClassifier com objetivo binario (binary:logistic)
- Metricas: Accuracy, Precision, Recall, F1-Score (weighted), AUC-ROC e metricas da classe Alta

## Parametros do XGBoost
- n_estimators: 300
- max_depth: 4
- learning_rate: 0.05
- subsample: 0.8
- colsample_bytree: 0.8
- min_child_weight: 1
- reg_lambda: 1.0
- eval_metric: logloss
- random_state: 42
- n_jobs: -1

## Saidas geradas
- metricas_slce3_base.csv
- matriz_confusao_slce3_base.png
- curva_roc_slce3_base.png
- comparacao_metricas_slce3_base.png
- evolucao_metricas_slce3_base.png
- metricas_classe_alta_slce3_base.png

## Observacoes
- Nao ha normalizacao, pois o XGBoost lida bem com escalas diferentes.
- O notebook usa o mesmo layout de graficos e relatorios adotado nos outros modelos de classificacao.
