from collection import deque
from SarIndicator import SarIndicator

class SarPoint(object):
    def __init__(self, idx, value):
        self.idx = idx
        self.value = value

class DrawLinesIndicator(object):
    def __init__(self, window=200, debug):
        self.BarSeries = deque(maxlen=window)
        self.Sar = SarIndicator()
        self.Peaks = deque(maxlen=window)
        self.Valleys = deque(maxlen=window)
        self.Indices = deque(maxlen=window)
        self.currentLineParams = dict(k=1, b=1) # 解析几何的直线公式
        self.IsReady = False
        self.Index = 0
        self.Debug = debug


    def Update(self, bar):
        self.BarSeries.appendleft(bar)
        self.Index += 1
        self.Sar.Update(bar)
        if not self.Sar.IsReady:
            return

        point_status = None
        this_point = None
        if self.Sar.CurrentColor == '红' and self.Sar.PreviousColor == "绿":
            point_status = "Peak"
            this_point = dict(x=self.Index - 1, y=bar.Close)
            self.Peaks.append(this_point)
            if len(self.Peaks) > 3:
                previous_base = self.Peaks[-3]
        else if self.Sar.CurrentColor == '绿' and self.Sar.PreviousColor == "红":
            point_status = "Valley"
            this_point = dict(x=self.Index - 1, y=bar.Close)
            self.Valleys.append(this_point)

        if point_status == "Peak" and len(self.Peaks) > 3 and len(self.Valleys) > 2 \
            and self.Peaks[-3]['y'] > self.Peaks[-2]['y'] > self.Peaks[-1]['y'] and self.Valleys[-2]['y'] > self.Valleys[-1]['y']:
            # 三顶两底，望短仓
            last3Peak = self.Peak[-3]
            self.calLineParam(last3Peak['x'], last3Peak['y'], this_point['x'], this_point['y'])
            self.Debug("短仓信号")
        elif point_status == "Valley" and len(self.Valleys) > 3 and len(self.Peaks) > 2 \
            and self.Valleys[-3]['y'] < self.Valleys[-2]['y'] < self.Valleys[-1]['y'] and self.Peaks[-2]['y'] > self.Peaks[-1]['y']:
            # 三底两顶，望长仓
            last3Valley = self.Valley[-3]
            self.calLineParam(last3Valley['x'], last3Valley['y'], this_point['x'], this_point['y'])
            self.Debug("长仓信号")
        else:
            self.currentLineParams = None

        if self.currentLineParams is not None:
            self.IsReady = True

    @property
    def Value(self):
        if self.currentLineParams:
            return self.currentLineParams['k'] * (self.Index - 1) + self.currentLineParams['b']
        return None

    def calLineParam(self, p1x, p1y, p2x, p2y):
        k = (p2y - p1y) / (p2x - p1x)
        b = (p1y*p2x - p2y*p1x) / (p2x - p1x)
        self.currentLineParams = dict(k=k, b=b)
