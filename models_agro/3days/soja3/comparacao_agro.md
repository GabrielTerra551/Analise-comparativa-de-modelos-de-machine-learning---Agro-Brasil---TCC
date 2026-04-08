# Relatório: Integração de Indicadores Agrícolas em XGBoost SOJA3

## ✓ Tarefa Concluída

### Arquivo Modificado
- **Notebook:** `models_agro/3days/soja3/xgboost_soja3.ipynb`
- **Status:** Atualizado e testado ✓

### Dados Utilizados
- **Dataset:** `indicadores_de_mercado_mais_indicadores_agro.csv`
- **Linhas:** 868 (mesmas do baseline)
- **Features adicionadas:** 8 novas (apenas com "lag")

### Features Agregadas

**Base (4):**
- Close, Low, High, Open

**Câmbio USD/BRL (4 com lag):**
- cambio_close_lag_1d, cambio_close_lag_3d, cambio_close_lag_6d, cambio_close_lag_10d

**Soja Chicago (4 com lag):**
- soja_chicago_close_lag_1d, soja_chicago_close_lag_3d, soja_chicago_close_lag_6d, soja_chicago_close_lag_10d

**Total: 12 features**

### Tratamento de Dados
- Forward fill aplicado: 25 NaNs em soja_chicago
- Método: `fillna(method='ffill')`
- Resultado: 868 linhas mantidas (sem perda de dados)

### Resultados - Comparação

#### ACCURACY SCORE
| Horizonte | Baseline | Agro    | Ganho Abs | Ganho %  |
|-----------|----------|---------|-----------|----------|
| 3 dias    | 0.6034   | 0.6609  | +0.0575   | **+9.5%** |
| 7 dias    | 0.5517   | 0.7069  | +0.1552   | **+28.1%** |
| 15 dias   | 0.6724   | 0.8506  | +0.1782   | **+26.5%** |
| 30 dias   | 0.6379   | 0.9023  | +0.2644   | **+41.4%** |

**Média:** +26.4%

#### AUC-ROC SCORE
| Horizonte | Baseline | Agro    | Ganho Abs | Ganho % |
|-----------|----------|---------|-----------|---------|
| 3 dias    | 0.5868   | 0.7069  | +0.1200   | **+20.5%** |
| 7 dias    | 0.5865   | 0.7492  | +0.1627   | **+27.7%** |
| 15 dias   | 0.7481   | 0.9329  | +0.1848   | **+24.7%** |
| 30 dias   | 0.7080   | 0.9491  | +0.2411   | **+34.1%** |

**Média:** +26.5%

### Métricas Mantidas (Comparação Igualitária)
✓ Accuracy (weighted)
✓ Precision (weighted)
✓ Recall (weighted)
✓ F1-Score (weighted)
✓ AUC-ROC
✓ Precision (Alta)
✓ Recall (Alta)
✓ F1-Score (Alta)

### Arquivos Gerados
- `metricas_soja3_agro.csv` - Tabela de métricas
- `matriz_confusao_soja3_agro.png` - 4 matrizes de confusão
- `curva_roc_soja3_agro.png` - 4 curvas ROC
- `comparacao_metricas_soja3_agro.png` - Gráfico comparativo
- `evolucao_metricas_soja3_agro.png` - Evolução temporal
- `metricas_classe_alta_soja3_agro.png` - Métricas classe positiva

### Caminho do Dataset
**De:** `models_agro/3days/soja3/`
**Para:** `../../../indicadores_agro/indicador_agro_tratado/join_indicadores_de_mercado/indicadores_de_mercado_mais_indicadores_agro.csv` ✓

### Conclusões
1. ✓ Features de lag (não close do mesmo dia) selecionadas corretamente
2. ✓ Tratamento de NaNs com forward fill bem-sucedido
3. ✓ Métricas idênticas permitem comparação justa
4. ✓ Ganho significativo de performance (+26% média)
5. ✓ Melhor desempenho no horizonte de 30 dias (+41.4%)

---

**Data:** 08/04/2026  
**Status:** ✓ Concluído
