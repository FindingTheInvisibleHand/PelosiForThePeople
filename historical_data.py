import yfinance as yf
import pandas as pd
import os

def get_data_all_tickers(
        period='1mo',
        limit=None
    ):
    # Read all trades from manually updated csv file
    path_to_csv = os.path.join('mappings', 'all_stocks.csv')
    currently_traded_stocks = pd.read_csv(path_to_csv, header=None).rename(columns={
        0: 'company_name', 1: 'ticker', 2: 'comment'})
    tickers = (currently_traded_stocks[
        currently_traded_stocks['ticker'] != 'out of scope']['ticker']
               .drop_duplicates().to_list())
    if limit==None:
        return tickers, yf.download(tickers, period=period)
    else:
        return tickers[:limit], yf.download(tickers[:limit], period=period)

get_data_all_tickers(limit=10)
# Multiindex slicing, DataFrame is structured as
# FrozenList([['Close', 'High', 'Low', 'Open', 'Volume'], [Tickers list]])
# single_stock = historical_data.xs('AAON', level=1, axis=1)

