import yfinance as yf
import pandas as pd
import os

# Lista de tickers (adicione ".SA" para ações da B3)
# tickers = ["SOJA3.SA", "SLCE3.SA", "LAND3.SA", "TTEN3.SA", "AGXY3.SA", "AGRO3.SA", "SMTO3.SA", "VITT3.SA"]
tickers = ["ZS=F", "BRL=X"]

start_date = "2018-01-01"
end_date = "2024-12-31" 

for ticker in tickers:
    print(f"Baixando dados de: {ticker}...")
    
    # Baixar dados
    # O progress=False evita poluir o console com barras de carregamento
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if not data.empty:
        # Ajuste no nome do arquivo:
        # Substituímos caracteres que podem dar erro no Windows/Linux (: ou =)
        file_name = ticker.replace(".SA", "").replace("=F", "_FUT").replace("=X", "_BRL")
        
        # Salvar em CSV no mesmo diretório do script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, f"{file_name}.csv")
        data.to_csv(file_path)
        print(f"Arquivo {file_name}.csv salvo com sucesso!")
    else:
        print(f"Aviso: Dados não encontrados para {ticker}")