from collections import deque
from System.Drawing import Color

class LongShortIndicator(object):

    def __init__(self, name, period):
        self.Time = datetime.min
        self.Name = name

        self.barSeries = deque(maxlen=period)

        # result series
        self.X = deque()
        self.LongShort = deque()
        self.ColorArray = deque()
        self.Color = Color.SkyBlue
        self.IsReady = False
        self.Value = 0

    def Update(self, data):
        newValue = (data.Close * 3 + data.High + data.Low + data.Open) / 6.0
        self.X.appendleft(newValue)
        self.Time = data.EndTime
        if len(self.X) < 23:
            return
        longShort = 0
        for i in range(0, 19):
            longShort += self.X[i] * (20 - i)
        longShort = (longShort + self.X[20]) / 210.0
        self.LongShort.appendleft(longShort)
        self.Value = longShort

        if len(self.LongShort) < 2:
            return
        color = Color.Purple if longShort > self.LongShort[1] else Color.DarkBlue
        self.Color = color
        self.ColorArray.appendleft(color)
        if len(self.ColorArray) >= 2:
            self.IsReady = True
