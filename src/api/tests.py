import yfinance as yf
import pandas as pd

# Télécharger les données du S&P 500 (^GSPC)
ticker = "^GSPC"
start_date = "1970-01-01"
end_date = "2025-07-27"

def download_sp500_daily_close():
    # Récupération des données
    data = yf.download(ticker, start=start_date, end=end_date)

    # Garder uniquement la colonne 'Close' et la renommer en 'close'
    df_close = data[['Close']].rename(columns={'Close': 'close'})

    # Réinitialiser l'index pour que la date soit une colonne
    df_close.reset_index(inplace=True)

    # Sauvegarde dans un fichier CSV
    df_close.to_csv("sp500_close.csv", index=False)
    print("Fichier 'sp500_close.csv' créé avec la colonne 'close'.")

def keep_only_equal_dates(final_path):
    path = "sp500_close.csv"
    path2 = "./src/backtester/data/csv/pe_ratio_sp500.csv"
    df1 = pd.read_csv(path, parse_dates=["Date"])
    print(df1.head())
    
    df2 = pd.read_csv(path2, parse_dates=["Date"], delimiter=';')
    print(df2.head())
    df3 = pd.merge(df2, df1, how='inner', on='Date')
    df3.to_csv(final_path)
    
keep_only_equal_dates("./src/backtester/data/csv/pe_ratio_full_sp500.csv")