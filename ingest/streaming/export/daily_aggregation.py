import pandas as pd, numpy as np
import datetime, os, copy
import util.logging as logging
from ingest.streaming.aggregation import Aggregation
from collections import deque

class DailyAggregation(Aggregation):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.trades = deque()

    def on_trade(self, trade):
        self.trades.append(trade)
        super().on_trade(trade)

    def on_bar_with_time(self, bar_with_time):
        self.bar_with_times.append(bar_with_time)
        super().on_bar_with_time(bar_with_time)

    def append_to_minute_csv(self, csv_file, epoch_seconds_start = None, epoch_seconds_end = None):
        for bwt in self.bar_with_times:
            epoch_seconds = int(bwt.time.timestamp())
            if epoch_seconds_start is not None and epoch_seconds < epoch_seconds_start:
                print('skipping as the timestamp {t} is before the bucket {bt}'.format(t=epoch_seconds, bt=epoch_seconds_start))
                continue
            if epoch_seconds_end is not None and epoch_seconds > epoch_seconds_end:
                print('skipping as the timestamp {t} is after the bucket {bt}'.format(t=epoch_seconds, bt=epoch_seconds_end))
                continue
            csv_file.write(','.join(map(lambda v: str(v), bwt.to_tuple_with_epoch_seconds())) + '\n')

    def append_to_rawdata_csv(self, csv_file, epoch_seconds_start = None, epoch_seconds_end = None):
        while len(self.trades) > 0:
            trade = self.trades.popleft()
            epoch_seconds = int(trade.timestamp_seconds)
            if epoch_seconds_start is not None and epoch_seconds < epoch_seconds_start:
                print('skipping as the timestamp {t} is before the bucket {bt}'.format(t=epoch_seconds, bt=epoch_seconds_start))
                continue
            if epoch_seconds_end is not None and epoch_seconds > epoch_seconds_end:
                print('skipping as the timestamp {t} is after the bucket {bt}'.format(t=epoch_seconds, bt=epoch_seconds_end))
                break
            csv_file.write(','.join(map(lambda v: str(v), trade.to_tuple_with_epoch_seconds())) + '\n')
