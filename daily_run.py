import compare_dates
import load_trades
from data_utils import bot_token, my_channel_id
import utils
import os
import time

import asyncio
import telegram
from datetime import datetime

if __name__ == '__main__':
    # create folder structure for 1st run
    folders_to_create = ['financial_disclosures', 'stock_purchases', 'other_documents']
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.mkdir(folder)

    all_trades = load_trades.get_and_format_all_trades()
    trades_with_tickers_df = load_trades.add_tickers(all_trades)
    write_location = os.path.join('stock_purchases', 'all_purchases')
    trades_with_tickers_df.to_csv(write_location, index=False)

    compare_dates.run()  # Automatically writes new files to appropriate locations
    today = datetime.today()
    new_trades = load_trades.get_specific_trades(today.strftime('%m_%d_%Y'))
    messages_list = utils.format_messages(new_trades)

    bot = telegram.Bot(token=bot_token)
    asyncio.run(utils.send_message(bot, my_channel_id, '-----------------------------------------\n\n '
                                                       'Update for: {} \n\n'

                                                       '-----------------------------------------'.format(
                                                        today.strftime("%m_%d_%Y, %H:%M:%S"))))

    if messages_list == []:
        asyncio.run(utils.send_message(bot, my_channel_id, 'No new trades today (or manual only, to check)'))
    else:
        if (len(messages_list) >= 100):
            batch_size = 30
            for n, message in enumerate(messages_list):
                asyncio.run(utils.send_message(bot, my_channel_id, message))
                if (n%30 == 0):
                    time.sleep(5)
        else:
            for message in messages_list:
                asyncio.run(utils.send_message(bot, my_channel_id, message))
