import re
import pandas as pd
import os

import load_trades

def check_new_trades():
    all_trades = load_trades.get_and_format_all_trades()

    stocks_path = os.path.join('mappings', 'all_stocks.csv')
    currently_available_stocks = pd.read_csv(stocks_path, header=None)
    currently_available_stocks.columns = ['stock_name', 'stock_ticker', 'comment']

    new_stocks = set(all_trades['stock_name'].unique()) - set(currently_available_stocks['stock_name'])

    if new_stocks in [set(), {None}]:
        print('No new stocks traded')
    else:
        print('following stocks to update in list: ')
        print(new_stocks)

def format_messages(new_trades):
    messages_list = []
    for entry in new_trades.itertuples():
        senator_name = re.split(r'(?=[A-Z])', entry[1])
        senator_name = ' '.join(filter(None, senator_name))
        stock_name = entry[2]
        buy_sell_flag = entry[3].strip() if (entry[3] is not None) else 'N/a'
        date = entry[4]
        messages_list.append('{0}: Traded {1} ({2}) on the {3}'.format(senator_name, stock_name, buy_sell_flag, entry[4]))

    return messages_list


async def send_message(bot, channel_id, message):
    async with bot:
        await bot.send_message(text=message, chat_id=channel_id)
