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



class Strat7c2(StrategyBase):
    def __init__(
        self, owner, sizer,
        percent_higher=2.0, percent_lower=2.0,
        rsi_period=14, rsi_overbought=50, rsi_oversold=50,
        slow_ma_period=99, fast_ma_period=25, v_fast_ma_period=12,
        tsi_period1=48, tsi_period2=36, tsi_thresh=0, tsi_movav=indicators.SMA
    ):

        self.p_l = percent_lower
        self.p_h = percent_higher

        self.prepare_to_buy = False
        self.prepare_to_sell = False

        self.under = False
        self.panic_flag = False

        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

        self.slow_ma_period = slow_ma_period
        self.fast_ma_period = fast_ma_period
        self.v_fast_ma_period = v_fast_ma_period

        self.tsi_period1 = tsi_period1
        self.tsi_period2 = tsi_period2
        self.tsi_movav = tsi_movav
        self.tsi_thresh = tsi_thresh

        super(Strat7c2, self).__init__(owner, sizer)

    def longest_period(self) -> int:
        return self.slow_ma_period + 16

    def start(self):
        self.np_closes = numpy.array(self.stream.close_values)
        self.rsi = talib.RSI(self.np_closes, self.rsi_period)
        self.tsi = indicators.TSI(self.tsi_period1, self.tsi_period2, 1, self.tsi_movav)
        #self.slow_ma = talib.SMA(self.np_closes, self.slow_ma_period)
        #self.fast_ma = talib.EMA(self.np_closes, self.fast_ma_period)
        #self.v_fast_ma = talib.TEMA(self.np_closes, self.v_fast_ma_period)
        self.slow_ma = indicators.SMA(self.slow_ma_period)
        self.fast_ma = indicators.EMA(self.fast_ma_period)
        self.v_fast_ma = indicators.TEMA(self.v_fast_ma_period)

        for i in range(16, -1, -1):
            if i != 0:
                self.tsi.next(self.stream.close_values[0:-i])
                self.slow_ma.next(self.stream.close_values[0:-i])
                self.fast_ma.next(self.stream.close_values[0:-i])
                self.v_fast_ma.next(self.stream.close_values[0:-i])
            else:
                self.tsi.next(self.stream.close_values)
                self.slow_ma.next(self.stream.close_values)
                self.fast_ma.next(self.stream.close_values)
                self.v_fast_ma.next(self.stream.close_values)

    def next(self) -> None:

        self.np_closes = numpy.array(self.stream.close_values)
        self.rsi = talib.RSI(self.np_closes, self.rsi_period)
        
        self.tsi.next(self.stream.close_values)
        self.slow_ma.next(self.stream.close_values)
        self.fast_ma.next(self.stream.close_values)
        self.v_fast_ma.next(self.stream.close_values)

        self.v_fast_ma_d1 = self.v_fast_ma[-1] - self.v_fast_ma[-8]
        self.v_fast_ma_d2 = self.v_fast_ma[-8] - self.v_fast_ma[-16]
        self.v_fast_ma_dd = self.v_fast_ma_d1 - self.v_fast_ma_d2
        
        self.fast_ma_d1 = self.fast_ma[-1] - self.fast_ma[-8]
        self.fast_ma_d2 = self.fast_ma[-8] - self.fast_ma[-16]
        self.fast_ma_dd = self.fast_ma_d1 - self.fast_ma_d2

        self.slow_ma_d1 = self.slow_ma[-1] - self.slow_ma[-8]
        self.slow_ma_d2 = self.slow_ma[-8] - self.slow_ma[-16]
        self.slow_ma_dd = self.slow_ma_d1 - self.slow_ma_d2
        
        self.tsi_d1 = self.tsi[-1] - self.tsi[-8]
        self.tsi_d2 = self.tsi[-8] - self.tsi[-16]
        self.tsi_dd = self.tsi_d1 - self.tsi_d2

        # Over/Under without order

        if (
            self.tsi[-1] < self.tsi_thresh and 
            not self.position and 
            not self.under
        ):
            if self.orders:
                self.panic_flag = True
            self.under = True

        if (
            self.tsi[-1] > self.tsi_thresh and 
            self.position
        ):
            self.under = False

        # Regular orders

        if not (self.prepare_to_buy and self.prepare_to_sell):

            # Prepare to buy conditions

            if (
                not self.position and 
                self.under and 
                not self.panic_flag and 
                self.rsi[-1] < self.rsi_oversold
            ) or (
                not self.position and 
                not self.under and 
                not self.panic_flag and 
                self.fast_ma_d1 > 0 and 
                self.fast_ma_d2 < 0 and 
                self.slow_ma_d1 > 0 and 
                self.rsi[-1] < self.rsi_oversold
            ) or (
                not self.position and 
                self.rsi[-1] < 10 and 
                self.tsi_dd > 0
            ) or (
                not self.position and 
                self.under and 
                self.v_fast_ma[-1] < self.fast_ma[-1] and 
                self.fast_ma_d1 > 0 and 
                self.slow_ma_dd > 0 and 
                self.rsi[-1] < 25
            ):
                self.prepare_to_buy = True

            

            # Prepare to sell conditions

            if (
                self.position and 
                not self.under and 
                self.v_fast_ma_d1 < 0 and 
                self.v_fast_ma_d2 > 0 and 
                self.slow_ma_dd < 0 and 
                self.rsi[-1] > self.rsi_overbought and 
                self.stream.close_values[-1] > self.orders[-1]['close_value'] * (1+(self.p_h/100.0))
            ) or (
                self.position and 
                self.rsi[-1] > 90
            ):
                self.prepare_to_sell = True



            # Prepare to buy conditions (TSI safenet)

            if (
                not self.position and 
                self.under and 
                self.tsi[-1] > self.tsi_thresh
            ):
                self.under = False
                self.panic_flag = False
                self.prepare_to_buy = True

            # Prepare to sell conditions (TSI safenet)

            if (
                self.position and 
                not self.under and 
                self.tsi[-1] < -self.tsi_thresh
            ):
                self.under = True
                self.panic_flag = True
                self.prepare_to_sell = True

            

        # Buy conditions

        if (
            self.prepare_to_buy
        ):
            self.prepare_to_buy = False
            self.buy()

        # Sell conditions

        if (
            self.prepare_to_sell
        ):
            self.prepare_to_sell = False
            self.sell()

    def info(self) -> dict:
        strat_info = {
            'name': '7c2',
            'params': {
                'RSI': float('%.2f' % self.rsi[-1]),
                'TSI': float('%.2f' % self.tsi[-1]),
                'SMA': float('%.2f' % self.slow_ma[-1]),
                'EMA': float('%.2f' % self.fast_ma[-1]),
                'TEMA': float('%.2f' % self.v_fast_ma[-1])
            }
        }
        return strat_info