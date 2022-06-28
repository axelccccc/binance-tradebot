import talib, numpy

from binance_tradebot import indicators

from .strategybase import StrategyBase



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