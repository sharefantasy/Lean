from clr import AddReference
AddReference("QuantConnect.Common")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Algorithm.Framework")
AddReference("QuantConnect.Indicators")

from QuantConnect import *
from QuantConnect.Indicators import *
from QuantConnect.Algorithm import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Alphas import *

from collections import deque
from datetime import timedelta
from enum import Enum
from .SarIndicator import SarIndicator
from .LongShortIndicator import LongShortIndicator
from .DrawLinesIndicator import DrawLinesIndicator
from .BottomTopIndicator import BottomTopIndicator


class CrossReferenceAlpha(AlphaModel):
    '''
    三项指标的交叉参照策略
    策略梗概
    1. 先用划线策略计算整体趋势，如果有明显的划线优势，则使用划线生产的信号(看看能不能写个description)
    2. 如果不满足划线策略，则观察底顶通道的趋势线。如果到了阈值点（短仓90，长仓10），则等待多空线信号，如果出现转色（短仓转蓝，长仓转紫），则转仓
    3. 如果颜色一直不变，则放置信号
    注意事项
    1. 就算划线策略中有趋势，其他数据和标志位都要计算,但是不能加入到信号中
    2. 需要配合止损模型使用。
    '''
    def __init__(self, window, symbol):
        insight_resolution = Resolution.Minute
        self.insight_period = Time.Multiply(Extensions.ToTimeSpan(insight_resolution), 1)
        self.barSeries = deque(maxlen=window)
        self.symbol = symbol

        self.sar = SarIndicator()
        self.longShort = LongShortIndicator()
        self.drawLines = DrawLinesIndicator()
        self.bottomTop = BottomTopIndicator()
        self.bottomTopMark = None

    def Update(self, algorithm, data):
        insights = set()
        bar = data[self.symbol]
        self.longShort.Update(bar)
        self.sar.Update(bar)
        self.drawLines.Update(bar)

        if not self.longShort.IsReady:
            return insights

        if not self.BottomTop.IsReady:
            return insights

        if not self.sar.IsReady:
            return insights

        # 是否需要出信号
        longInsight = Insight.Price(self.symbol, self.insight_period, InsightDirection.Up)
        shortInsight = Insight.Price(self.symbol, self.insight_period, InsightDirection.Down)

        # 计算画线规则
        if self.drawLines.IsReady:
            linePredictPrice = self.drawLines.CalPredicts()
            if bar.Close > linePredictPrice and algorithm.:
                insights = [longInsight]
            elif bar.Close < linePredictPrice:
                insights = [shortInsight]

        # 计算底顶规则
        if self.bottomTop.IsReady and len(insights) == 0:
            if self.bottomTop.Value >= 90:
                self.bottomTopMark =  '空'
            elif self.bottomTop.Value <= 10:
                self.bottomTopMark =  '多'

        if self.longShort.IsReady and len(insights) == 0:
            if self.bottomTopMark == '空' and self.longShort.CurrentColor == '蓝':
                insights.add(shortInsight)
            elif self.bottomTopMark == '多' and self.longShort.CurrentColor == '紫':
                insights.add(longInsight)

        return insights
