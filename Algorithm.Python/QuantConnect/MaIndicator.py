from collections import deque
from pykalman import KalmanFilter
from scipy import signal
import numpy as np
from Common import MockQuoteBar
from talib import SMA

class MAIndicator(object):

    def __init__(self, name, window, logFunc):
        self.data = deque(maxlen=window)
        self.Value = 0
        self.Color = None
        self.IsReady = False
        self.close = deque(maxlen=window)
        self.Debug = logFunc
        self.window = window
        self.name = name

    def Update(self, quoteBar):
        self.data.appendleft(quoteBar)
        self.close.append(quoteBar.Close)

        if len(self.data) < self.window:
            self.Value = None
            return

        value = SMA(to_np(self.close), self.window)
        self.Value = float(value[-1])
        self.IsReady = True


def to_np(ll):
    return np.array(ll)
