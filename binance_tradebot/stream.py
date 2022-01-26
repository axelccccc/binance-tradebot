from . import exceptions as exc
from . import utils
from .gui import format_rows

import datetime as dt

class Stream():

    def __init__(self, symbol: str, start_qty: float, interval: str, strategy: str, sizer: str):

        self.symbol = symbol.upper()
        self.start_qty = start_qty
        self.interval = interval

        self.name = symbol + '@kline_' + self.interval

        self.strategy = utils.instantiate('binance_tradebot.strategies', strategy, self, sizer)

        self.close_values = []

        from .api import _cga
        _cga.load_historical_klines(self, self.strategy.longest_period() + 1)

        self.strategy.start()

    def next(self):
        self.strategy.next()

    def __str__(self):

        rows = []

        rows.append(['Stream : ' + self.name])
        rows.append(['Close Value', '# Closes', 'Start Qty'])
        rows.append([f'{self.close_values[-1]}', f'{len(self.close_values)}', self.strategy.qty])

        return format_rows(rows)

_sga = None
""" Global Streams Aggregate variable\n
    Allows the rest of the system to access the instantiated 
    streams aggregate by importing this variable.\n
    Specifically designed to be accessed inside the WebSocket's `on_open()` """

class Streams():

    def __init__(self, config: dict):

        global _sga

        # if _sga:
        #     raise exc.MoreThanOneAggregate

        self.streams = []

        for i in range(0, len(config['markets'])):

            self.streams.append(
                Stream(
                    config['markets'][i], 
                    config['start_qties'][i], 
                    config['intervals'][i],
                    config['strategies'][i],
                    config['sizers'][i]
                    )
                )

        _sga = self
    
    def __getitem__(self, key):
        return self.streams[key]

    def __setitem__(self, key):
        return self.streams[key]

    def __len__(self):
        return len(self.streams)

    def process(self, json_message):
    
        if len(self.streams) > 1:

            candle = json_message['data']['k']
            candle_closed = candle['x']
            close_value = float(candle['c'])

            if candle_closed:

                for stream in self.streams:

                    if stream.name == json_message['stream']:

                        stream.close_values.append(close_value)
                        #pprint(stream.strategy.info())
                        stream.next()
        
        else:

            candle = json_message['k']
            candle_closed = candle['x']
            close_value = float(candle['c'])

            if candle_closed:

                self.streams[0].close_values.append(close_value)
                #pprint(self.streams[0].strategy.info())
                self.streams[0].next()

    def profits(self):

        self.overall_profit = 0.0
        self.total_stake = 0.0
        self.current_value = 0.0
        self.total_profit_percent = 0.0

        for stream in self.streams:
            if stream.strategy.orders:
                self.total_stake += stream.strategy.orders[0]['usd']
            
            self.overall_profit += stream.strategy.total_profit

            if self.total_stake != 0:
                self.total_profit_percent = (self.overall_profit / self.total_stake) * 100.0

            self.current_value = self.total_stake + self.overall_profit

            

        return {
            'total_stake': round(self.total_stake, 2), 
            'current_value': round(self.current_value, 2), 
            'overall_profit': round(self.overall_profit, 2), 
            'total_profit_percent': round(self.total_profit_percent, 2)
        }