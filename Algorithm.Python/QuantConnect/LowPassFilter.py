from collections import deque
from scipy import signal
from Common import MockQuoteBar


class LowPassFilter(object):

    def __init__(self, name, window, stop_frequency, sample_rate, logFunc):
        self.stop_frequency = stop_frequency
        self.sample_rate = sample_rate
        self.Name = name
        self.window = window
        self.data = deque(maxlen=window)
        self.close = deque(maxlen=window)
        self.filtered = deque(maxlen=window)
        self.Debug = logFunc
        self.IsReady = False
        self.Value = 0
        wc = self.stop_frequency / self.sample_rate
        self.butter = signal.butter(3, wc, 'low')

    def Update(self, quoteBar):
        self.data.appendleft(quoteBar)
        self.close.append(quoteBar.Close)
        if len(self.close) < self.window:
            self.Value = quoteBar.Close
            return

        filter = signal.filtfilt(self.butter[0], self.butter[1], self.close)
        self.Value = float(filter[-1])
        self.filtered.appendleft(self.Value)
        if len(self.filtered) > 2:
            self.IsReady = True

    @property
    def LastBar(self):
        if not self.IsReady:
            return None
        bar = MockQuoteBar()
        lastBar = self.data[0]
        bar.Close = self.Value
        bar.Open = self.filtered[1]
        bar.High = lastBar.High
        bar.Low = lastBar.Low
        bar.EndTime = lastBar.EndTime
        return bar
