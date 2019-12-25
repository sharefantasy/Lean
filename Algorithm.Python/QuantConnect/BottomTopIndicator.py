from collections import deque
from talib import SMA, EMA

class BottomTopIndicator(object):
    def __init__(self, name, period):
        self.Name = name
        self.Time = deque(maxlen=period)

        self.barSeries = deque(maxlen=period)
        self.baseWindow = 55
        self.Peroid = period

        # result series
        self.L1 = deque(maxlen=period)
        self.H1 = deque(maxlen=period)
        self.Resistence = deque(maxlen=period)
        self.Support = deque(maxlen=period)
        self.Midium = deque(maxlen=period)
        # V11 compute group
        self.V11 = deque(maxlen=period)
        self.WindowPercentSma = deque(maxlen=5)
        self.ClosePercentSma = deque(maxlen=5)
        self.TwoOrderWindowCloseSma = deque(maxlen=3)
        self.Trend = deque(maxlen=period)
        self.IsReady = False
        self.Value = 0

    def Update(self, bar):
        self.Time.appendleft(bar.Time)
        self.barSeries.appendleft(bar)
        P1 = bar.High - bar.Low

        resistence = bar.Low + P1 * (7 / 8)
        support = bar.Low + P1 * (0.5 / 8)
        medium = (resistence + support) / 2

        self.Resistence.appendleft(resistence)
        self.Support.appendleft(support)
        self.Medium.appendleft(medium)
        if not self.isV11Ready():
            return

        V11 = self.CurrentV11()
        self.V11.appendleft(V11)
        if len(self.V11) < 3:
            return

        trend = EMA(self.V11[:3:-1])
        self.Trend.appendleft(trend)
        self.Value = trend
        self.IsReady = True

    @property
    def BarLow(self):
        return [bar.Low for bar in self.barSeries[self.baseWindow]]

    @property
    def BarHigh(self):
        return [bar.High for bar in self.barSeries[self.baseWindow]]

    def isV11Ready(self):
        return len(self.BarHigh) >= (self.baseWindow + self.ClosePercentSma.maxlen + self.TwoOrderWindowCloseSma.maxlen)


    def CurrentV11(self):
        HHV55 = max(*self.BarHigh)
        LLV55 = max(*self.BarLow)
        percent = (self.barSeries[0].Close - LLV55) / (HHV55 - LLV55) * 100
        self.WindowPercentSma.append(percent)
        closePercentSma = SMA(self.WindowPercentSma)
        self.ClosePercentSma.append(closePercentSma)
        twoOrderSma = SMA(self.ClosePercentSma)
        self.TwoOrderWindowCloseSma.append(twoOrderSma)

        return 3 * closePercentSma - 2 * twoOrderSma
