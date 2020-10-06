import util.logging
import statistics
from strategy.factors.bar_with_times_factors.factor import BarWithTimesFactor
from strategy.bar_with_times_strategy.strategy import BarWithTimesTradeStrategy
from collections import defaultdict

class MoveStat:
    def __init__(self, window_seconds, change):
        self.window_seconds = window_seconds
        self.change = change

class MoveStats(BarWithTimesFactor):
    def __init__(self, symbol, aggregation):
        super().__init__(symbol, aggregation)
        self.stats = defaultdict(list)

    def __str__(self):
        def for_ws(ws, ss):
            return 'mean: {m}%, median: {md}%, 1: {m1}%, 10: {m10}%, 90: {m90}%, 99: {m99}%, stdev: {stdev}%'.format(
                m=round(self.get_mean(ws) * 100, 3),
                md=round(self.get_median(ws) * 100, 3),
                m1=round(self.get_percentile(ws, 1) * 100, 3),
                m10=round(self.get_percentile(ws, 10) * 100, 3),
                m90=round(self.get_percentile(ws, 90) * 100, 3),
                m99=round(self.get_percentile(ws, 99) * 100, 3),
                stdev=round(self.get_stdev(ws) * 100, 3),
            )
        return '\n'.join(['{w}: '.format(w=ws//60) + for_ws(ws, ss) for ws, ss in self.stats.items()])

    def print(self):
        print(str(self))

    def conbime(self, stats):
        for w, ss in stats.items():
            self.stats[w] += ss

    def add_stat(self, stat):
        self.stats[stat.window_seconds].append(stat)

    def _get_change_list(self, window_seconds):
        return map(lambda s: s.change, self.stats[window_seconds])

    def get_mean(self, window_seconds):
        return statistics.mean(self._get_change_list(window_seconds))

    def get_median(self, window_seconds):
        return statistics.median(self._get_change_list(window_seconds))

    def get_percentile(self, window_seconds, percentile):
        return statistics.quantiles(self._get_change_list(window_seconds), n=101)[percentile]

    def get_stdev(self, window_seconds):
        return statistics.stdev(self._get_change_list(window_seconds))


class MoveStatCollectStrategy(BarWithTimesTradeStrategy):
    def __init__(self, positionsize, symbol, current_time = None):
        super().__init__(positionsize, symbol, None, None, None, None, current_time=current_time)
        self.move_stats = MoveStats(symbol, self.aggregation)

    def on_new_timebucket(self):
        super().on_new_timebucket()

    # override
    def on_trade(self, trade):
        self.aggregation.on_trade(trade)
        self.on_ingest()

    # override
    def on_bar_with_time(self, bar_with_time):
        self.aggregation.on_bar_with_time(bar_with_time)
        self.on_ingest()

    # override
    def on_ingest(self):
        windows = [5, 10, 15, 20]
        for w in windows:
            change = self.move_stats.get_change('close', change_window_minutes = w, query_range_minutes = 1)
            change = round(change, 3)
            self.move_stats.add_stat(MoveStat(w * 60, change))

        super().on_ingest()

    def on_daily_trade_end(self):
        self.move_stats.print()
