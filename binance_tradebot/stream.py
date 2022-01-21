from . import config as cfg
from . import exceptions as exc
from . import utils
from . import api
from .gui import format_rows

import datetime as dt

class Stream():

    def __init__(self, symbol: str, start_qty: float, interval: str, strategy: str, sizer: str):

        self.symbol = symbol.upper()
        self.start_qty = start_qty
        self.interval = interval

        self.name = symbol + '@kline_' + self.interval

        self.strategy = utils.instantiate('binance_tradebot.strategy', strategy, self, sizer)

        self.close_values = []

        api.load_historical_klines(self, self.strategy.longest_period() + 1)

        self.strategy.start()

    def next(self):
        self.strategy.next()

    def __str__(self):

        rows = []

        rows.append(['Stream : ' + self.name])
        rows.append(['Close Value', '# Closes', 'Start Qty'])
        rows.append([f'{self.close_values[-1]}', f'{len(self.close_values)}', self.strategy.qty])

        return format_rows(rows)


_streams_global_access = None
""" Global Streams Aggregate variable\n
    Allows the rest of the system to access the instantiated 
    streams aggregate by importing this variable.\n
    Specifically designed to be accessed inside the WebSocket's `on_open()` """

class Streams():

    def __init__(self):

        global _streams_global_access

        if _streams_global_access:
            raise exc.MoreThanOneAggregate

        if cfg.bot_is_configured:

            self.streams = []

            for i in range(0, len(cfg.MARKETS)):

                self.streams.append(
                    Stream(
                        cfg.MARKETS[i], 
                        cfg.START_TRADE_QTIES[i], 
                        cfg.INTERVALS[i],
                        cfg.STRATEGIES[i],
                        cfg.SIZERS[i]
                        )
                    )

            _streams_global_access = self

        else:
            raise exc.BotNotConfigured
            
    
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