#########################################
# BINANCE TRADING BOT
#
# For SPOT Trading & Market Orders
# Supports multiple simulatenous streams
#
#########################################

from binance_tradebot.bot import TradeBot



def main():

    my_bot = TradeBot()
    my_bot.start()



if __name__ == "__main__":

    try:
        main()
    
    except Exception as err:
        print(err)