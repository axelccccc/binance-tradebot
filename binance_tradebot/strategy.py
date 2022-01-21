import talib, numpy
from binance.enums import *
from datetime import datetime

from binance_tradebot.config import ORDERS_DATA_PATH

# from . import indicators as ind
from .api import order
from .data import load_orders, format_order, save_data
from .utils import instantiate
from .gui import format_rows
from .notif import send_order_notif

# Strategies shall have default values for strategy related parameters (all but symbol, start_qty)

class StrategyBase():

    def __init__(self, owner, sizer) -> None:

        self.stream = owner
        
        self.qty = self.stream.start_qty

        self.sizer = instantiate('binance_tradebot.sizer', sizer, self)

        """ @property
        def close_values(self):
            return self.stream.close_values """
        
        self.orders = load_orders(self.stream.symbol)

        if len(self.orders):
            if self.orders[-1]['side'] == 'SELL':
                self.position = False
            else:
                self.position = True
        else:
            self.position = False

        self.trade_profit = 0.0
        self.total_profit = 0.0

        if len(self.orders) >= 2:
            self.trade_profit = self.orders[-1]['usd'] - self.orders[-2]['usd']
            for i in range(1, len(self.orders)):
                self.total_profit += self.orders[i]['usd'] - self.orders[i-1]['usd']

    def longest_period(self) -> int:
        """Returns the longest period of data an indicator requires.\n
        Used to load the appropriate number of past klines into memory."""
        pass

    def order(self, side):
        
        if self.orders:
            self.sizer.resize()

        o = order(self.stream.symbol, side, self.qty)

        if o:
            if side == SIDE_BUY:
                self.position = True
            else: # SIDE_SELL
                self.position = False
                
            self.orders.append(format_order(o, self.stream.close_values[-1]))

            if len(self.orders) >= 2:
                self.trade_profit = self.orders[-1]['usd'] - self.orders[-2]['usd']
                self.total_profit += self.trade_profit

            save_data(self.orders, ORDERS_DATA_PATH, 'w')

            send_order_notif(self)


    def buy(self):
        self.order(SIDE_BUY)

    def sell(self):
        self.order(SIDE_SELL)

    def start(self):
        """Precalculations before starting the strategy"""
        pass

    def next(self) -> None:
        pass

    def info(self) -> dict:
        """Returns strategy indicators & parameters as a dict.
        \nFor display purposes."""
        if self.orders:
            last_order = self.orders[-1]
        else:
            last_order = []

        strat_info = {
            'name': '',
            'last_order': last_order,
            'last_trade_profit': self.trade_profit,
            'total_profit': self.total_profit,
            'params': {},
            'sizer': self.sizer.sizer_info()
        }
        return strat_info

    def __str__(self):

        info = self.info()

        rows = []
        rows.append(['Strategy : ' + info['name']])
        h_strat_sliced = []
        r_strat_sliced = []
        for param, value in info['params'].items():
            if len(h_strat_sliced) == 5:
                rows.append(h_strat_sliced)
                rows.append(r_strat_sliced)
                h_strat_sliced = []
                r_strat_sliced = []
            h_strat_sliced.append(param)
            r_strat_sliced.append(value)
        rows.append(h_strat_sliced)
        rows.append(r_strat_sliced)
        
        if self.orders:
            rows.append(['Last Order : ' + datetime.fromtimestamp(
                self.orders[-1]['time']/1000
                ).strftime("%d-%m-%Y %H:%M")])
            rows.append(['Side', 'Price', 'Qty', 'Value', 'Close Value'])
            rows.append([
                self.orders[-1]['side'],
                self.orders[-1]['price'],
                self.orders[-1]['qty'],
                '%.2f$' % self.orders[-1]['usd'],
                self.orders[-1]['close_value']
                ])

        if len(self.orders) >= 2:
            total_profit_percent = self.total_profit * 100.0 / self.orders[0]['usd']
            rows.append(['Last Trade Profit', 'Total Trade Profit', '%'])
            rows.append([
                '%.2f$' % self.last_trade_profit,
                '%.2f$' % self.total_profit,
                f"{total_profit_percent}%"
            ])
        
        return format_rows(rows)



class BasicRSI(StrategyBase):

    def __init__(self, owner, sizer, rsi_period=14, rsi_oversold=30, rsi_overbought=70) -> None:
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.rsi = []

        super(BasicRSI, self).__init__(owner, sizer)

    def longest_period(self) -> int:
        return self.rsi_period

    def start(self):
        self.np_closes = numpy.array(self.stream.close_values)
        self.rsi = talib.RSI(self.np_closes, self.rsi_period)

    def next(self) -> None:

        if len(self.stream.close_values) >= self.rsi_period:

            self.np_closes = numpy.array(self.stream.close_values)
            self.rsi = talib.RSI(self.np_closes, self.rsi_period)

            if (
                self.rsi[-1] > self.rsi_overbought and 
                self.position
            ):
                self.sell()
            elif (
                self.rsi[-1] < self.rsi_oversold and 
                not self.position
            ):
                self.buy()

    def info(self) -> dict:
        strat_info = {
            'name': 'Basic RSI',
            'params': {
                'RSI': (round(self.rsi[-1],2) if len(self.rsi) else 0.0),
                'RSI Period': self.rsi_period,
                'RSI Overbought': self.rsi_overbought,
                'RSI Oversold': self.rsi_oversold
            }
        }
        return strat_info