from collections import deque
from scipy import signal
import numpy as np
from Common import MockQuoteBar
from talib import SAR

class SarIndicator(object):

    def __init__(self, name, window, a, b, logFunc):
        self.data = deque(maxlen=window)
        self.value = 0
        self.IsReasy = False
        self.high = deque(maxlen=window)
        self.low = deque(maxlen=window)
        self.Debug = logFunc
        self.a = a
        self.b = b
        self.window = window
        self.name = name
        self.colorarry = deque(maxlen=window)
        self.Color = None

    def Update(self, quoteBar):
        self.data.appendleft(quoteBar)
        self.high.append(quoteBar.High)
        self.low.append(quoteBar.Low)

        if len(self.data) < self.window:
            self.Value = quoteBar.Close
            return

        value = SAR(to_np(self.high), to_np(self.low), self.a, self.b)
        self.Value = float(value[-1])
        color = '红' if value <= quoteBar.Close else '绿'
        self.colorarry.appendleft(color)
        self.IsReady = True


def to_np(ll):
    return np.array(ll)
