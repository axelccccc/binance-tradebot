import imp
import telebot
from datetime import datetime

from .private import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)

def send_order_notif(strategy):

    message = """
~~~Order Executed~~~

Time
{}

Market          Side   
{}              {}
Price           Value   
{}              {}$

Trade profit    (%)  
{}$             {}%
""".format(
    datetime.fromtimestamp(
        strategy.orders[-1]['time']/1000
        ).strftime("%d-%m-%Y %H:%M"),
        strategy.orders[-1]['symbol'],
        strategy.orders[-1]['side'],
        strategy.orders[-1]['price'],
        strategy.orders[-1]['usd'],
        strategy.trade_profit,
        str((strategy.orders[-1]['usd'] - strategy.orders[-2]['usd']) \
            * 100.0 / strategy.orders[-2]['usd'])
)
    bot.send_message(TELEGRAM_USER_ID, message)