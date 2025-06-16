import glob
import os
import pandas as pd
from read_pdf import read_pdf
from data_utils import formatted_invested_amount_dict


def get_specific_trades(business_date):
    path_to_folder = os.path.join('stock_purchases', business_date, "*pdf")
    daily_trades = glob.glob(path_to_folder)
    # daily_trades.remove('stock_purchases\\05_23_2025\\WhitesidesGeorge_20027982.pdf')
    # daily_trades.remove('stock_purchases\\05_23_2025\\DoggettLloyd_20030285.pdf')

    all_stocks_df = pd.DataFrame()
    for path in daily_trades:
        df = read_pdf(path)
        representative_name = path.split(sep='\\')[-1].split(sep='_')[0]
        df.insert(0, 'representative_name', representative_name)
        all_stocks_df = pd.concat([all_stocks_df, df])

    if all_stocks_df.empty:
        print('Document probably filled manually, to check')
        return pd.DataFrame()

    all_stocks_df['formatted_inv_amount'] = all_stocks_df['invested_amount'].str.split('-').str[0].str.strip().map(formatted_invested_amount_dict)
    all_stocks_df['min_amount'] = all_stocks_df['formatted_inv_amount'].str.split('-').str[0].astype(float)
    all_stocks_df['max_amount'] = all_stocks_df['formatted_inv_amount'].str.split('-').str[1].astype(float)
    all_stocks_df.drop(['invested_amount', 'formatted_inv_amount'], inplace=True, axis=1)

    return all_stocks_df.reset_index(drop=True)

def get_and_format_all_trades():
    doc_paths = []
    stock_purchases = os.listdir('stock_purchases')

    for entry in stock_purchases:
        path = os.path.join('stock_purchases', entry, "*pdf")
        doc_paths += glob.glob(path)

    # For the time being, removing whitesides and doggett as their files are poorly formatted
    files_to_remove = ['WhitesidesGeorge_20027982.pdf', 'DoggettLloyd_20030285.pdf']
    for file in files_to_remove:
        path = os.path.join('stock_purchases', '05_23_2025', file)
        if os.path.exists(path):
            doc_paths.remove(path)

    all_trades_df = pd.DataFrame()
    for path in doc_paths:
        df = read_pdf(path)
        representative_name = path.split(sep='\\')[-1].split(sep='_')[0]
        df.insert(0, 'representative_name', representative_name)
        all_trades_df = pd.concat([all_trades_df, df])

    if not all_trades_df.empty:
        all_trades_df['formatted_inv_amount'] = all_trades_df['invested_amount'].str.split('-').str[0].str.strip().map(formatted_invested_amount_dict)
        all_trades_df['min_amount'] = all_trades_df['formatted_inv_amount'].str.split('-').str[0].astype(float)
        all_trades_df['max_amount'] = all_trades_df['formatted_inv_amount'].str.split('-').str[1].astype(float)
        all_trades_df.drop(['invested_amount', 'formatted_inv_amount'], inplace=True, axis=1)

    return all_trades_df.reset_index(drop=True)

def add_tickers(trades_df):
    trades_copy = trades_df.copy()
    trades_with_tickers = pd.DataFrame()

    if not trades_copy.empty:
        path_to_csv = os.path.join('mappings', 'all_stocks.csv')
        name_to_ticker_mapping = pd.read_csv(path_to_csv, header=None).rename(columns={
            0: 'stock_name', 1: 'ticker', 2: 'comment'})

        trades_with_tickers = trades_copy.merge(name_to_ticker_mapping[['stock_name', 'ticker']],on='stock_name', how='left')
        trades_with_tickers['purchase_date'] = pd.to_datetime(trades_with_tickers['purchase_date'])

    return trades_with_tickers

































































