import clr
clr.AddReference("System")
clr.AddReference("QuantConnect.Algorithm")
clr.AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *

from collections import deque
from datetime import timedelta
from LongShortWithMA21Indicator import LongShortWithMA21Indicator
from LongShortIndicator import LongShortIndicator

from Common import PlotAdapter, ColorPlotAdapter, LinePlotter
from System.Drawing import Color
from LowPassFilter import LowPassFilter
from SarIndicator import SarIndicator
from DrawLinesIndicator import DrawLinesIndicator

from BottomTopIndicator import BottomTopIndicator

from MAIndicator import MAIndicator
from LongShortWithMA21Indicator import LongShortWithMA21Indicator
from MA5Indicator import MA5Indicator

class CustomizeAlphaAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetCash(20000)           #Set Strategy Cash

        self.SetStartDate(2019, 9, 13)   #Set Start Date
        self.SetEndDate(2019, 9, 14)    #Set End Date
        self.SetWarmUp(timedelta(days=1))

        self.SetTimeZone("Asia/Shanghai")

        future = self.AddFuture(Futures.Metals.Gold)
        future.SetFilter(timedelta(0), timedelta(31))

        self.symbol = Futures.Energies.CrudeOilWTI # 加入cl的security


        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)
        self.sar = SarIndicator("sar", 30, 0.02, 0.3, self.Debug)
        self.drawline = DrawLinesIndicator("drawline", 2000, self.Debug, self.sar)
        self.longshort = LongShortWithMA21Indicator("多空线", 30)

        self.pic = Chart('pic')
        self.AddPic()

        self.SarPlotter = ColorPlotAdapter(self.Plot, self.pic, "sar1", SeriesType.Scatter, ScatterMarkerSymbol.Diamond)
        self.DrawLinePlotter = LinePlotter(self.pic, "drawline", Color.Blue)
        self.longshortPloter = ColorPlotAdapter(self.Plot, self.pic, 'longshort', SeriesType.Scatter, ScatterMarkerSymbol.Circle)

        self.consolidators = dict()
        self.currentContract = None
        self.contractsSet = set()

        self.fastPeriod = 1
        self.normalPeriod = 5
        self.slowPeriod = 15

        self.changed = 0

        self.PriceMap = {}


    def OnData(self, data):
        pass

    def OnDataFastConsolidated(self, sender, quoteBar):
        pass

    def OnDataNormalConsolidated(self, sender, quoteBar):
        self.DoTrade(quoteBar)
        pass

    def OnDataSlowConsolidated(self, sender, quoteBar):
        pass

    def DoTrade(self, quoteBar):
        self.longshort.Update(quoteBar)
        self.sar.Update(quoteBar)
        if self.sar.IsReady:
            self.SarPlotter.Plot(self.sar.Value, self.sar.CurrentColor)

        self.drawline.Update(self.UtcTime, quoteBar)

        if self.drawline.IsReady:
            f = self.drawline.FirstPoint
            s = self.drawline.SecondPoint
            self.DrawLinePlotter.Plot(f.time, f.y, s.time, s.y)
            self.drawline.clear()


    def closeSymbol(self, symbol):
        holdings = self.Portfolio[symbol].Quantity
        if abs(holdings) > 0:
            self.MarketOrder(symbol, -holdings)

    def formatSymbols(self, contracts):
        return  [{"symbol": x.Symbol.Value, "expiry": x.Expiry } for x in contracts]

    def PlotPrice(self, symbol, value):
        if symbol not in self.PriceMap:
            self.PriceMap[symbol] = PlotAdapter(self.Plot, self.pic, symbol, SeriesType.Line, Color.Tan)
        self.PriceMap[symbol].Plot(value)

    def OnSecuritiesChanged(self, changes):
        contract = changes.AddedSecurities[0]
        newsymbols = self.formatSymbols(changes.AddedSecurities)
        self.Debug(f"new symbol: {newsymbols}")

        if contract is not None:
            oldContract = self.currentContract
            self.Debug("Choose symbol: {}".format(contract.Symbol.Value))
            self.currentContract = contract

            # 如果换合约，需要先清了之前的单
            if oldContract is not None and oldContract != contract:
                self.removeContract(oldContract)

            for period, OnDataFunc in zip([self.fastPeriod, self.normalPeriod, self.slowPeriod], \
                [self.OnDataFastConsolidated, self.OnDataNormalConsolidated, self.OnDataSlowConsolidated]):
                consolidator = QuoteBarConsolidator(timedelta(minutes=period))
                consolidator.DataConsolidated += OnDataFunc
                self.SubscriptionManager.AddConsolidator(contract.Symbol, consolidator)
                if contract.Symbol not in self.consolidators:
                    self.consolidators[contract.Symbol] = []
                self.consolidators[contract.Symbol].append(consolidator)

        for contract in changes.RemovedSecurities:
            self.removeContract(contract)

    def removeContract(self, contract):
        currentSymbol = self.currentContract.Symbol
        self.Debug(f"Conctract {contract.Symbol.Value} cleared")
        self.closeSymbol(currentSymbol)
        consolidators = self.consolidators.pop(contract.Symbol)
        for c in consolidators:
            self.SubscriptionManager.RemoveConsolidator(contract.Symbol, c)

    def AddPic(self):
        self.pic.AddSeries(Series('Buy', SeriesType.Scatter, '$', Color.Red, ScatterMarkerSymbol.Triangle))
        self.pic.AddSeries(Series('Sell', SeriesType.Scatter, '$', Color.Blue, ScatterMarkerSymbol.TriangleDown))

        self.AddChart(self.pic)
