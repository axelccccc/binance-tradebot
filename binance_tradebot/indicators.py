import math

# Probably going to only use TSI for now, the other indicators are
# available through TA-Lib



class IndicatorBase():
    def __init__(self):
        self.data = []



# Basic Operations

class Average(IndicatorBase):
    def __init__(self, period: int):
        self.period = period
        super().__init__()

    def next(self, data) -> float:
        self.data.append(math.fsum(data[-self.period::]) / self.period)
        return self.data[-1]

class ExponentialSmoothing(Average):
    def __init__(self, period: int, alpha=None):
        if alpha is None:
            self.alpha = 2.0 / (1.0 + period)
        self.alpha1 = 1.0 - self.alpha
        super().__init__(period)

    def prenext(self, data):
        super().next(data)

    def next(self, data) -> float:
        self.prenext(data)
        self.data.append(self.data[-2] * self.alpha1 + data[-1] * self.alpha)
        return self.data[-1]



# Moving Averages

class SMA(IndicatorBase):
    def __init__(self, period: int):
        self.av = Average(period)
        super().__init__()

    def next(self, data) -> float:
        self.data.append(self.av.next(data))
        return self.data[-1]

class EMA(IndicatorBase):
    def __init__(self, period):
        self.es = ExponentialSmoothing(period)
        super(EMA, self).__init__()

    def next(self, data) -> float:
        self.data.append(self.es.next(data))
        return self.data[-1]

class SMMA(IndicatorBase):
    def __init__(self, period):
        self.es = ExponentialSmoothing(period, alpha=(1.0 / period))
        super(SMMA, self).__init__()

    def next(self, data) -> float:
        self.data.append(self.es.next(data))
        return self.data[-1]

class DEMA(IndicatorBase):
    def __init__(self, period):
        self.ema1 = EMA(period)
        self.ema2 = EMA(period)
        super(DEMA, self).__init__()

    def next(self, data) -> float:
        e1 = self.ema1.next(data)
        e2 = self.ema2.next(self.ema1.data)
        self.data.append(2.0 * e1 - e2)
        return self.data[-1]

class TEMA(IndicatorBase):
    def __init__(self, period):
        self.ema1 = EMA(period)
        self.ema2 = EMA(period)
        self.ema3 = EMA(period)
        super(TEMA, self).__init__()

    def next(self, data) -> float:
        e1 = self.ema1.next(data)
        e2 = self.ema2.next(self.ema1.data)
        e3 = self.ema3.next(self.ema2.data)
        self.data.append(3.0 * e1 - 3.0 * e2 + e3)
        return self.data[-1]





# Strength Indicators

class TSI(IndicatorBase):
    def __init__(self, period1, period2, pchange):
        self.period1 = period1
        self.period2 = period2
        self.pchange = pchange

        self.pc = []
        self.pc_abs = []

        self.ema1 = EMA(period1)
        self.ema12 = EMA(period2)
        self.ema2 = EMA(period1)
        self.ema22 = EMA(period2)

        super(TSI, self).__init__()

    def next(self, data) -> float:
        self.pc.append(data[-1] - data[-self.pchange-1])
        self.pc_abs.append(abs(self.pc[-1]))

        self.ema1.next(self.pc)
        sm12 = self.ema12.next(self.ema1.data)
        self.ema2.next(self.pc_abs)
        sm22 = self.ema22.next(self.ema2.data)

        self.data.append(100.0 * (sm12 / sm22))