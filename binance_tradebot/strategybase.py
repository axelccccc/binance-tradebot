from binance.enums import *
from datetime import datetime

# from . import indicators as ind
from .api import _cga
from . import data
from .utils import instantiate
from .gui import format_rows
from .notifications import send_order_notif

# Strategies shall have default values for strategy related parameters (all but symbol, start_qty)

class StrategyBase():

    def __init__(self, owner, sizer) -> None:

        self.stream = owner
        
        self.qty = self.stream.start_qty

        self.sizer = instantiate('binance_tradebot.sizers', sizer, self)

        """ @property
        def close_values(self):
            return self.stream.close_values """
        
        self.orders = data.load_orders(self.stream.symbol)

        if len(self.orders):
            if self.orders[-1]['side'] == 'SELL':
                self.position = False
            else:
                self.position = True
        else:
            self.position = False

        self.trade_profit = 0.0
        self.total_profit = 0.0

        if (
            len(self.orders) >= 2 and 
            self.orders[-1]['side'] == 'SELL'
        ):
            self.trade_profit = self.orders[-1]['usd'] - self.orders[-2]['usd']
            for i in range(1, len(self.orders), 2):
                self.total_profit += self.orders[i]['usd'] - self.orders[i-1]['usd']

    def longest_period(self) -> int:
        """Returns the longest period of data an indicator requires.\n
        Used to load the appropriate number of past klines into memory."""
        pass

    def order(self, side):
        
        if self.orders:
            if side == SIDE_BUY:
                self.sizer.resize_buy()
            else: # SIDE_SELL
                self.sizer.resize_sell()
        else:
            self.qty = self.sizer.format_qty(self.qty)

        o = _cga.order(self.stream.symbol, side, self.qty)

        if o:
            if side == SIDE_BUY:
                self.position = True
            else: # SIDE_SELL
                self.position = False
                
            self.orders.append(data.format_order(o, self.stream.close_values[-1]))

            if len(self.orders) >= 2:
                self.trade_profit = self.orders[-1]['usd'] - self.orders[-2]['usd']
                self.total_profit += self.trade_profit

            data.save_data(self.orders, data.orders_data_path(), 'w')

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

        rows.append([''])
        strat_rows = format_rows(rows)
        sizer_rows = str(self.sizer) + '\n'

        rows = []
        
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
            rows.append([''])

        if len(self.orders) >= 2:
            total_profit_percent = self.total_profit * 100.0 / self.orders[0]['usd']
            rows.append(['Last Profit', 'Total Profit', '%'])
            rows.append([
                '%.2f$' % self.trade_profit,
                '%.2f$' % self.total_profit,
                f"{round(total_profit_percent, 2)}%"
            ])
        
        orders_rows = format_rows(rows)

        return strat_rows + sizer_rows + orders_rows