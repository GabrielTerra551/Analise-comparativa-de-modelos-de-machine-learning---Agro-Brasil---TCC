# Comparação de Estratégias de Treinamento - XGBoost SOJA3

## 📊 Resumo das Estratégias

### 1. **soja3/** - Stratified Random Split (Padrão)
- **Método:** `train_test_split()` com `stratify=y_clean` e `random_state=42`
- **Split:** 80% treino / 20% teste (aleatório, balanceado)
- **Embaralhamento:** SIM - dados aleatorizados
- **Realismo:** Menor - assume que treino e teste vêm da mesma distribuição

### 2. **soja3_temporal/** - Time Series Split (Cronológico)
- **Método:** Divisão índice `X_clean.iloc[:split_idx]` e `X_clean.iloc[split_idx:]`
- **Split:** 80% treino / 20% teste (primeiros/últimos cronologicamente)
- **Embaralhamento:** NÃO - ordem temporal preservada
- **Realismo:** MAIOR - simula previsão no tempo (treino = passado, teste = futuro)

---

## 📈 Resultados Comparativos - Accuracy

| Horizonte | Aleatório | Temporal | Diferença | % Change |
|-----------|-----------|----------|-----------|----------|
| **3 dias**   | 0.6034    | 0.5402   | -0.0632   | **-10.5%** |
| **7 dias**   | 0.5517    | 0.5287   | -0.0230   | **-4.2%**  |
| **15 dias**  | 0.6724    | 0.5230   | -0.1494   | **-22.2%** |
| **30 dias**  | 0.6379    | 0.2529   | -0.3850   | **-60.3%** |

### 💡 Interpretação

**Gap observado:** O modelo temporal apresenta accuracy **10.5% a 60.3% menor** que o aleatório.

**Por quê?**
1. **Data Leakage Reduzido:** Stratified split pode capturar padrões globais. Time series não.
2. **Mudanças de Mercado:** Dados de 80% histórico → 20% futuro sofrem alterações nas condições
3. **Distribuição Diferente:** Treino e teste vêm de períodos distintos (viés não-estacionariedade)
4. **Melhor Simulação Real:** Time series split é mais realista para previsão financeira

---

## 🎯 Qual Usar?

### Use **Aleatório (soja3/)** quando:
- ✅ Objetivo é **comparar desempenho relativo** entre modelos
- ✅ Dados estacionários ou com padrões globais
- ✅ Validação cruzada estratificada desejada

### Use **Temporal (soja3_temporal/)** quando:
- ✅ **Previsão real** é o objetivo
- ✅ Dados são **séries temporais** (preços, indicadores)
- ✅ Quer **validar realismo** do modelo
- ✅ Precisa entender degradação futura

---

## 📁 Estrutura

```
models_agro/3days/
├── soja3/                    # Estratégia Aleatória (Padrão)
│   └── xgboost_soja3.ipynb
│
├── soja3_temporal/           # Estratégia Temporal (Time Series)
│   └── xgboost_soja3_temporal.ipynb
│
└── COMPARACAO_ESTRATEGIAS_TREINO.md  # Este arquivo
```

---

## 🔍 Métricas Adicionais

### AUC-ROC Comparativo

| Horizonte | Aleatório | Temporal | Gap   |
|-----------|-----------|----------|-------|
| 3 dias    | 0.5868    | 0.5991   | +0.01 |
| 7 dias    | 0.5865    | 0.5572   | -0.03 |
| 15 dias   | 0.7481    | 0.6497   | -0.10 |
| 30 dias   | 0.7080    | 0.6458   | -0.06 |

---

## 🚀 Próximas Etapas

1. **Análise de Série Temporal:** Aplicar ARIMA, Prophet, LSTM para melhor capturar dinâmicas
2. **Walk-Forward Validation:** Múltiplas janelas temporais para maior robustez
3. **Estudar Causas:** Investigar correlação entre período treino/teste
4. **Ensemble:** Combinar ambas estratégias para previsões mais robustas

---

## 📌 Notas

- **Features utilizadas:** 19 (4 base + 7 técnicos + 8 lags agrícolas)
- **Dataset:** SOJA3_tratado.csv + Câmbio USD/BRL + Soja Chicago (lags)
- **Hiperparâmetros:** Iguais em ambas estratégias (xgb_params)
- **Random State:** 42 (aleatório e temporal usam mesmos parâmetros XGBoost)

---

**Conclusão:** O modelo temporal é mais conservador e realista, mas ambas as estratégias são válidas para diferentes propósitos. A análise comparativa ajuda a compreender a **robustez** do modelo em cenários reais.
