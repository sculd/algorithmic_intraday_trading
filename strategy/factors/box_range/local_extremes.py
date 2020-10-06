from ingest.streaming.aggregation import Aggregation
from strategy.factors.factor import Factor
from collections import deque
import util.current_time

class LocalExtremesParameter:
    def __init__(self,
                 window_minutes
                 ):
        self.window_minutes = window_minutes

class LocalExtremesFactor(Factor):
    def __init__(self, symbol, bar_with_times, param, current_time = None):
        super().__init__(symbol)
        self.aggregation = Aggregation(symbol)
        self.aggregation.bar_with_times = bar_with_times
        self.param = param
        self.current_time = current_time if current_time else util.current_time.CurrentTime()
        self.trades = deque()

    def on_trade(self, trade):
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        self.trades.append(trade)
        while True:
            if len(self.trades) == 0:
                break
            if self.trades[0].timestamp_seconds >= epoch_seconds - self.param.window_minutes * 60:
                break
            self.trades.popleft()

    def get(self):
        upper, lower = 0, 1000 * 1000
        for trade in self.trades.copy():
            if trade.price > upper:
                upper = trade.price
            if trade.price < lower:
                lower = trade.price
        return upper, lower


