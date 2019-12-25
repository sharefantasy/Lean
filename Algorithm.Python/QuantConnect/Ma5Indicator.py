from collections import deque
import numpy as np
from Common import MockQuoteBar
from talib import SMA, EMA, STDDEV
from System.Drawing import Color


class MA5Indicator(object):

    def __init__(self, name, logFunc):
        self.data = deque(maxlen=10)
        self.Value = 0
        self.Color = None
        self.IsReady = False
        self.close = deque(maxlen=12)
        self.Debug = logFunc
        self.window = 5
        self.name = name
        self.valueArray = deque(maxlen=22)

        self.volArray = deque(maxlen=22)
        self.v1Array  = deque(maxlen=22)
        self.v2Array  = deque(maxlen=22)
        self.cysArray = deque(maxlen=22)
        self.v2TcysArray = deque(maxlen=22)


    def Update(self, quoteBar):
        self.data.appendleft(quoteBar)
        self.close.append(quoteBar.Close)

        if len(self.data) < self.window:
            self.Value = None
            return

        value = SMA(to_np(self.close), 5)
        self.Value = float(value[-1])
        self.valueArray.appendleft(self.Value)

        if len(self.valueArray) < 2:
            return

        self.Color = Color.White
        # 标记绿色
        last_value = self.valueArray[1]
        if self.Value < last_value:
            self.Color = Color.Green
            self.IsReady = True
            return

        close_vol = (quoteBar.LastAskSize + quoteBar.LastBidSize) / 2
        v1 = quoteBar.Close * close_vol
        self.volArray.append(close_vol)
        self.v1Array.append(v1)
        if len(self.v1Array) < 13 or len(self.volArray) < 13:
            return

        curV1 = float(EMA(to_np(self.v1Array), 13)[-1])
        emaVol = float(EMA(to_np(self.volArray), 13)[-1])
        curV2 = float(curV1 / emaVol)
        self.v2Array.append(curV2)
        v2Tcys = (quoteBar.Close - curV2) / curV2
        self.v2TcysArray.append(v2Tcys)
        cys = v2Tcys * 100
        self.cysArray.append(cys)

        if len(self.cysArray) < 20:
            return

        midd = float(SMA(to_np(self.cysArray), 20)[-1])
        cc = midd + 0.85 * float(STDDEV(to_np(self.cysArray), 10)[-1])
        self.Debug(f'cys: {cys}, cc: {cc}')
        if cys > cc:
            self.Color = Color.Red

        self.IsReady = True


def to_np(ll):
    return np.array(ll)
