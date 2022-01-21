from binance.client import Client
from binance.enums import *
from binance.exceptions import *

from . import config as cfg

# client = None
# For intellisense — uncomment only during coding
client = Client(cfg.API_KEY, cfg.API_SECRET, testnet=cfg.TESTNET)



def order(symbol, side, quantity, order_type=ORDER_TYPE_MARKET): # side is buy or sell
        try:
            print("sending order")
            order = client.create_order(symbol=symbol,
                                        side=side,
                                        type = order_type,
                                        quantity=quantity,
                                        #price=price,
                                        newOrderRespType='FULL')
            #pprint.pprint(order)
        except BinanceRequestException as e:
            print("Request exception")
            return None
        except BinanceAPIException as e:
            print('API Exception')
            print(e.status_code)
            print(e.message)
            return None
        except BinanceOrderMinPriceException as e:
            print('BinanceOrderMinPriceException')
            return None
        except BinanceOrderException as e:
            print('BinanceOrderException')
            return None
        else:
            return order



def load_historical_klines(stream, offset):

    time_unit = stream.interval[-1]
    time_multiplier = int(stream.interval[0:-1])

    if time_unit == 'm':
        date_start = str(offset*time_multiplier) + " minutes ago UTC"
    elif time_unit == 'h':
        date_start = str(offset*time_multiplier) + " hours ago UTC"
    elif time_unit == 'd':
        date_start = str(offset*time_multiplier) + " days ago UTC"
    elif time_unit == 'w':
        date_start = str(offset*time_multiplier) + " weeks ago UTC"
    elif time_unit == 'M':
        date_start = str(offset*time_multiplier) + " months ago UTC"

    klines = client.get_historical_klines(stream.symbol, stream.interval, date_start)
    
    for kline in klines:
        stream.close_values.append(float(kline[4]))



def get_cash_balance():
    balance = client.get_asset_balance(asset=cfg.DOLLAR)
    return float(balance['free'])