# Random Forest - SOJA3 (Dataset Dummy)

Este modelo segue o mesmo padrao visual e de relatorios usado nos notebooks de classificacao existentes.

## Decisoes e configuracoes
- Dataset: datasets_dummy/classificacao/SOJA3_tratado.csv
- Features: Close, Low, High, Open
- Targets: target_3d, target_7d, target_15d, target_30d (binario: 1 = Alta, 0 = Baixa/Estavel)
- Split: 80/20 com estratificacao e random_state=42
- Modelo: RandomForestClassifier
- Metricas: Accuracy, Precision, Recall, F1-Score (weighted), AUC-ROC e metricas da classe Alta

## Parametros do Random Forest
- n_estimators: 300
- max_depth: None
- min_samples_split: 2
- min_samples_leaf: 1
- max_features: sqrt
- random_state: 42
- n_jobs: -1

## Saidas geradas
- metricas_soja3_dummy.csv
- matriz_confusao_soja3_dummy.png
- curva_roc_soja3_dummy.png
- comparacao_metricas_soja3_dummy.png
- evolucao_metricas_soja3_dummy.png
- metricas_classe_alta_soja3_dummy.png

## Observacoes
- Nao ha normalizacao, pois o Random Forest lida bem com escalas diferentes.
