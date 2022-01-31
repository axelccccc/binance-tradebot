#########################################
# BINANCE TRADING BOT
#
# For SPOT Trading & Market Orders
# Supports multiple simulatenous streams
#
#########################################

import datetime as dt

from binance_tradebot.bot import TradeBot


def main():

    my_bot = TradeBot()
    my_bot.start()



if __name__ == "__main__":

    try:
        main()
    
    except KeyboardInterrupt:
        from binance_tradebot.telegram import _tga
        print("finished.")
        time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        _tga.telebot.send_message(_tga.main_bot.config['telegram_user_id'], ("Bot finished by user at %s" % time))
    except Exception as err:
        _tga.telebot.send_message(_tga.main_bot.config['telegram_user_id'], ("Bot raised error: %s" % err))