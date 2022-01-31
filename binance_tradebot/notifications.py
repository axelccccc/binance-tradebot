from datetime import datetime

def send_order_notif(strategy):

    from .telegram import _tga

    message = """
~~~Order Executed~~~

Time
{}

Market
{}
Side
{}

Price
{}
Qty
{}
Close
{}
Value                   
{}$

Trade profit        (%)  
{}$                 {}%
""".format(
    datetime.fromtimestamp(
        strategy.orders[-1]['time']/1000
        ).strftime("%d-%m-%Y %H:%M"),
        strategy.orders[-1]['symbol'],
        strategy.orders[-1]['side'],
        strategy.orders[-1]['price'],
        strategy.orders[-1]['qty'],
        strategy.orders[-1]['close_value'],
        strategy.orders[-1]['usd'],
        '%.2f' % round(strategy.trade_profit, 2),
        '%.2f' % round((strategy.orders[-1]['usd'] - strategy.orders[-2]['usd']) \
            * 100.0 / strategy.orders[-2]['usd'], 2) if len(strategy.orders) >= 2 else 0.00
)
    _tga.telebot.send_message(_tga.main_bot.config['telegram_user_id'], message)