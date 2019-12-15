
# pythonnet entrance
from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Algorithm.Framework")
AddReference("QuantConnect.Common")
from System import *
from QuantConnect import *
from QuantConnect.Orders import *
from QuantConnect.Algorithm import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Alphas import *
from QuantConnect.Algorithm.Framework.Execution import *
from QuantConnect.Algorithm.Framework.Portfolio import *
from QuantConnect.Algorithm.Framework.Risk import *
from QuantConnect.Algorithm.Framework.Selection import *
from QuantConnect.Securities import *


# python imports
from datetime import timedelta, datetime
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import mpl_finance as mpf


class CustomPlottingAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.FullData = pd.DataFrame()
        self.Debug("trade start")
        # Set requested data resolution
        future = self.AddFuture(Futures.Metals.Gold)
        future.SetFilter(timedelta(0), timedelta(31))

        self.SetStartDate(2019, 9, 10)   #Set Start Date
        self.SetEndDate(2019, 9, 11)    #Set End Date
        self.SetCash(20000)           #Set Strategy Cash
        # self.longshort = LongShortWithMA21Indicator("多空线", 30)
        # self.fastkalman = KFIndicator("快卡尔曼滤波", 20, self.Debug)
        # self.lowPass = LowPassFilter("低通滤波", 30, 0.005, 60, self.Debug)
        # self.sar = SarIndicator("sar", 30, 0.02, 0.3, self.Debug)
        # self.ma5 = MA5Indicator("ma5", self.Debug)
        # self.ma21 = MAIndicator("ma21", 21, self.Debug)

    def Ondata(self, bar):
        current_data = (dict(
            Time=bar.Time,
            Open=bar.Open,
            Close=bar.Close,
            High=bar.High,
            Low=bar.Low,
        ))

        current_data.update(dict(
            ma20=20,
            longshort=20,
            bottomTop=20,
        ))


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

    def OnEndOfAlgorithm(self):
        time_idx = self.FullData["Time"]
        fig = plt.figure(figsize=(24, 0))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_x_ticks(range(0, time_idx), 5000)
        ax.set_xticklabels(time_idx[::5000])
        # draw basic candle stick graph
        mpf.candlestick2_ochl(ax,
                              self.FullData["Open"],
                              self.FullData["Close"],
                              self.FullData["High"],
                              self.FullData["Low"],
                              colorup='r', colordown='green',
                              width=0.5,
        )

        # draw indices
        # ma20
        ma20_index = self.FullData["Ma20"]
        ax.plot(ma20_index, label="ma20")
        # 多空线
        longshort_index = self.FullData["LongShort"]
        ax.plot(longshort_index, label="longshort")
        # 底顶通道
        bottomTop_index = self.FullData["BottomTop"]
        ax.plot(bottomtop_index, label="bottomtop")

        fig.show()
