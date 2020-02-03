from collection import deque
from SarIndicator import SarIndicator
from System.Drawing import Color

class SarPoint(object):
    def __init__(self, time, x, y):
        self.time = time
        self.x = x
        self.y = y

    def __str__(self):
        return "<{}, {}, {}>".format(self.time, self.x, self.y)


# 划线指标, 由多个画线规则组成的指标，也有多个产出
class DrawLinesIndicator(object):
    def __init__(self, name, window, debug, sar):
        self.Name = name
        self.Sar = sar
        # Sar中的顶点与底点
        self.Peaks = deque(maxlen=window)
        self.Valleys = deque(maxlen=window)

        # 下方index是先加的，为了保证实际索引从0开始，初始化为-1
        self.Index = -1
        self.Debug = debug

        # 最终结果，3-2顶底组合，划线成型后的解析几何直线公式
        # 对于3-2顶底组合式的式子，主要是为了使直线公式成型，其Value值自然也是延长线的计算值
        self.FirstPoint = None
        self.SecondPoint = None
        self.Direction = None
        self.IsReady = False # 此处IsReady只作最终划线结果使用，仅表示是否产生了划线

        # 中间结果
        # 当前点是否顶或底
        self.SpecialPoint = None

        # 2-2顶底性质
        self.IsLesserReady = False
        self.LesserValue = None

    def Update(self, UtcTime, bar):
        self.Index += 1
        if not self.Sar.IsReady:
            return

        # 计算当前点是否顶底（特征点）
        point_status = None
        currentPoint = None
        if self.Sar.CurrentColor == Color.Green and self.Sar.PreviousColor == Color.Red:
            point_status = "Peak"
            currentPoint = SarPoint(UtcTime, self.Index, self.Sar.Value)
            self.Peaks.appendleft(currentPoint)
            self.Debug("Peak, {}".format(currentPoint))
            self.SpecialPoint = dict(t="Peak", p=currentPoint)

        elif self.Sar.CurrentColor == Color.Red and self.Sar.PreviousColor == Color.Green:
            point_status = "Valley"
            currentPoint = SarPoint(UtcTime, self.Index, self.Sar.Value)
            self.Valleys.appendleft(currentPoint)
            self.Debug("Valley, {}".format(currentPoint))
            self.SpecialPoint = dict(t="Valley", p=currentPoint)
        else:
            self.SpecialPoint = None

        # 初始化一些值
        peaksLen = len(self.Peaks)
        valleysLen = len(self.Valleys)
        self.IsReady = False

        # 计算是否满足顶底划线
        if point_status == "Peak":
            # 计算是否三顶两底，短仓
            if peaksLen > 3 and valleysLen > 2 \
                and self.Peaks[2].y > self.Peaks[1].y > self.Peaks[0].y \
                and self.Valleys[1].y > self.Valleys[0].y:
                    self.FirstPoint = self.Peaks[2]
                    self.SecondPoint = currentPoint
                    self.Direction = "短"
                    self.IsReady = True
                    self.Debug("短仓信号，{} {}".format(self.FirstPoint, self.SecondPoint))

            # 计算是否短仓的两顶两底
            elif peaksLen > 2 and valleysLen > 2 \
                and self.Peaks[1].y > self.Peaks[0].y \
                and self.Valleys[1].y > self.Valleys[0].y:
                    self.IsLesserReady = True
                    self.LesserValue = "短"

        elif point_status == "Valley":
            # 计算是否三底两顶，长仓
            if valleysLen > 3 and peaksLen > 2 \
                and self.Valleys[2].y < self.Valleys[1].y < self.Valleys[0].y \
                and self.Peaks[1].y < self.Peaks[0].y:
                self.FirstPoint = self.Valleys[2]
                self.SecondPoint = currentPoint
                self.Direction = "长"
                self.IsReady = True
                self.Debug("长仓信号，{} {}".format(self.FirstPoint, self.SecondPoint))

            # 计算是否长仓的两顶两底
            elif valleysLen > 2 and peaksLen > 2 \
                and self.Valleys[1].y < self.Valleys[0].y \
                and self.Peaks[1].y < self.Peaks[0].y:
                    self.IsLesserReady = True
                    self.LesserValue = "长"

        # 不满足底顶划线规则
        if not self.IsLesserReady:
            self.LesserValue = None

    # 外部手动清除记录点
    def clear(self):
        self.IsReady = False
        self.FirstPoint = None
        self.SecondPoint =  None
        self.Direction = None


    # 从两点式计算当前延长线的值
    @property
    def Value(self):
        if self.FirstPoint is not None and self.SecondPoint is not None:
            x1 = self.FirstPoint.x
            y1 = self.FirstPoint.y
            x2 = self.SecondPoint.x
            y2 = self.SecondPoint.y

            k = (y2 - y1) / (x2 - x1)
            b = (y1 * x2 - y2 * x1) / (x2 - x1)
            return k * self.Index + b
        return None
