import pandas as pd
import numpy as np
from pathlib import Path

# Define paths
base_dir = Path(__file__).parent.parent.parent.parent
soja3_path = base_dir / "datasets" / "datasets_indicadores" / "classificacao" / "SOJA3_tratado.csv"
cambio_path = base_dir / "indicadores_agro" / "indicador_agro_tratado" / "Cambio_USD_BRL.csv"
soja_chicago_path = base_dir / "indicadores_agro" / "indicador_agro_tratado" / "Soja_Chicago_USD_Bushel.csv"
output_path = Path(__file__).parent / "indicadores_de_mercado_mais_indicadores_agro.csv"

# Load datasets
print("Carregando datasets...")
soja3 = pd.read_csv(soja3_path)
cambio = pd.read_csv(cambio_path)
soja_chicago = pd.read_csv(soja_chicago_path)

# Standardize date column names and convert to datetime
soja3['Date'] = pd.to_datetime(soja3['Date'])
cambio['Data'] = pd.to_datetime(cambio['Data'])
soja_chicago['Data'] = pd.to_datetime(soja_chicago['Data'])

# Rename date columns for consistency
cambio = cambio.rename(columns={'Data': 'Date'})
soja_chicago = soja_chicago.rename(columns={'Data': 'Date'})

# Keep only 'close' from cambio and soja_chicago
cambio_close = cambio[['Date', 'close']].copy()
soja_chicago_close = soja_chicago[['Date', 'close']].copy()

# Rename close columns for clarity
cambio_close = cambio_close.rename(columns={'close': 'cambio_close'})
soja_chicago_close = soja_chicago_close.rename(columns={'close': 'soja_chicago_close'})

# Create lags for cambio (-1, -3, -6, -10 days)
print("Criando lags para câmbio...")
for lag in [1, 3, 6, 10]:
    cambio_close[f'cambio_close_lag_{lag}d'] = cambio_close['cambio_close'].shift(lag)

# Create lags for soja chicago (-1, -3, -6, -10 days)
print("Criando lags para soja Chicago...")
for lag in [1, 3, 6, 10]:
    soja_chicago_close[f'soja_chicago_close_lag_{lag}d'] = soja_chicago_close['soja_chicago_close'].shift(lag)

# Merge all datasets
print("Unindo datasets...")
# First merge soja3 (left) with cambio (right)
merged = soja3.merge(cambio_close, on='Date', how='left')

# Then merge with soja_chicago (right)
merged = merged.merge(soja_chicago_close, on='Date', how='left')

# Sort by date
merged = merged.sort_values('Date').reset_index(drop=True)

# Display info ANTES de limpeza
print(f"\nResumo da fusão (ANTES da limpeza):")
print(f"  - Linhas SOJA3: {len(soja3)}")
print(f"  - Linhas Câmbio: {len(cambio)}")
print(f"  - Linhas Soja Chicago: {len(soja_chicago)}")
print(f"  - Linhas resultado: {len(merged)}")
print(f"  - NaNs totais: {merged.isna().sum().sum()}")

# Define critical features (features usadas no treinamento)
critical_features = ['Close', 'Low', 'High', 'Open',
                     'OBV', 'FWMA', 'TEMA', 'HLC3', 'BB_upper', 'BB_middle', 'BB_lower',
                     'cambio_close_lag_1d', 'cambio_close_lag_3d', 'cambio_close_lag_6d', 'cambio_close_lag_10d',
                     'soja_chicago_close_lag_1d', 'soja_chicago_close_lag_3d', 'soja_chicago_close_lag_6d', 'soja_chicago_close_lag_10d']

# Identificar linhas incompletas
incomplete_rows = merged[critical_features].isna().any(axis=1)
print(f"\nLinhas incompletas (com NaN em features críticas): {incomplete_rows.sum()}")
if incomplete_rows.sum() > 0:
    print(f"  Datas afetadas: {merged[incomplete_rows]['Date'].dt.strftime('%Y-%m-%d').tolist()}")

# Limpar dataset (remover linhas com NaN em features críticas)
print("\nLimpando dataset (dropna em features críticas)...")
merged_clean = merged[~incomplete_rows].reset_index(drop=True)

# Display sample
print(f"\nAmostra das primeiras linhas com novos dados de mercado:")
market_cols = ['Date'] + [col for col in merged_clean.columns if 'cambio' in col or 'soja_chicago' in col]
print(merged_clean[market_cols].head(15))

# Display info DEPOIS de limpeza
print(f"\nResumo APÓS limpeza:")
print(f"  - Linhas antes: {len(merged)}")
print(f"  - Linhas depois: {len(merged_clean)}")
print(f"  - Linhas removidas: {len(merged) - len(merged_clean)} ({(len(merged) - len(merged_clean))/len(merged)*100:.1f}%)")
print(f"  - NaNs totais: {merged_clean.isna().sum().sum()}")

# Save output
print(f"\nSalvando resultado em: {output_path}")
merged_clean.to_csv(output_path, index=False)
print("✓ Concluído!")
