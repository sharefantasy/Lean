from System.Drawing import Color
from enum import Enum
import talib
import numpy


class OrderStatus(Enum):
    STAY = 0
    BUY = 1
    SELL = 2
    COVER = 3


def genIndicator(func):
    def __inner__(series, n, isOutArray=False):
        """

        :type series: BaseSeries
        """
        array = series.array
        if len(array) < n:
            raise SeriesNotReady(series)
        result = func(numpy.array(array, "double"), n)
        if isOutArray:
            return result
        else:
            return result[-1]

    return __inner__


EMA = genIndicator(talib.EMA)
SMA = genIndicator(talib.SMA)
STD = genIndicator(talib.STDDEV)
# Your New Python File



class MockQuoteBar(object):
    def __init__(self,):
        self.Close = 0
        self.High = 0
        self.Low = 0
        self.Open = 0
        self.EndTime = None


class PlotAdapter(object):

    def __init__(self, plot_func, chart, basename, series_type, color):
        self.plot_func = plot_func
        self.basename = basename
        self.buffer = [0]
        self.series_type = series_type
        self.color = color
        self.chart = chart

        self.NewSeries()

    def Plot(self, value):
        currentIdx = len(self.buffer) - 1
        if self.buffer[currentIdx] >= 3950:
            self.NewSeries()
        seriesName = f'{self.basename}_{currentIdx}_Price'
        self.plot_func(self.chart.Name, seriesName, value)
        self.buffer[currentIdx] += 1

    def NewSeries(self):
        currentIdx = len(self.buffer) - 1
        self.buffer.append(0)
        currentIdx += 1
        self.chart.AddSeries(Series(f'{self.basename}_{currentIdx}_Price',  self.series_type, '$', self.color))

class ColorPlotAdapter(object):

    def __init__(self, plot_func, chart, basename, series_type, marker_symbol=None):
        self.plot_func = plot_func
        self.basename = basename
        self.buffer = {}
        self.series_type = series_type
        self.chart = chart
        self.marker_symbol = marker_symbol

    def Plot(self, value, color):
        if color not in self.buffer:
            self.buffer[color] = [0]

        currentIdx = len(self.buffer[color]) - 1
        currentIdxSize = self.buffer[color][currentIdx]
        if currentIdxSize == 0 or currentIdxSize >= 3950:
            self.NewSeries(color)

        seriesName = self.GetSeriesKey(currentIdx, color)
        self.plot_func(self.chart.Name, seriesName, value)
        self.buffer[color][currentIdx] += 1

    def GetSeriesKey(self, index, color):
        return '{}_{}_{}'.format(self.basename, str(color), index)

    def NewSeries(self, color):
        currentIdx = len(self.buffer[color]) - 1
        self.buffer[color].append(0)
        currentIdx += 1
        self.chart.AddSeries(Series(self.GetSeriesKey(currentIdx, color),  \
            self.series_type, '$', color, self.marker_symbol))
