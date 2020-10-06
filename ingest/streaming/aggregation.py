import pandas as pd, numpy as np
import datetime, os
from collections import deque
import pytz
import util.logging as logging
from enum import Enum

_TIME_ZONE_US_EASTERN = 'US/Eastern'

_BAR_WITH_TIMES_MAX_LENGTH = 60 * 5

class BAR_INTERVAL(Enum):
    ONE_MINUTE = 1

class BAR_WITH_TIME_COMBINE_MODE(Enum):
    REPLACE = 1
    AGGREGATE = 2


class Trade:
    def __init__(self, timestamp_seconds, symbol, price, volume):
        self.timestamp_seconds, self.symbol, self.price, self.volume = timestamp_seconds, symbol, price, volume

    def __str__(self):
        return 'epoch_seconds: {t}, symbol: {s}, price: {p}, volume: {v}'.format(
            t = self.timestamp_seconds, s = self.symbol, p = self.price, v = self.volume
        )

    @staticmethod
    def get_tuple_names():
        return ('timestamp_seconds',) + ('symbol', 'price', 'volume',)

    def to_tuple_with_epoch_seconds(self):
        return (int(self.timestamp_seconds),) + (self.symbol, self.price, self.volume,)

class Bar:
    def __init__(self, symbol, open_, high, low, close_, volume):
        self.symbol, self.open, self.high, self.low, self.close, self.volume = symbol, open_, high, low, close_, volume

    def __str__(self):
        return 'symbol: {s}, o: {o}, l: {l}, h: {h}, c: {c}, volume: {v}'.format(
            s = self.symbol, o = self.open, l = self.low, h = self.high, c = self.close, v = self.volume
        )

    def new_bar_with_trade(symbol, price, volume):
        return Bar(symbol, price, price, price, price, volume)

    def on_trade(self, trade):
        if self.symbol != trade.symbol:
            raise Exception('symbol mismatch')
        self.high = max(self.high, trade.price)
        self.low = min(self.low, trade.price)
        self.close = trade.price
        self.volume += trade.volume

    @staticmethod
    def get_tuple_names():
        return ('symbol', 'open', 'high', 'low', 'close', 'volume',)

    def to_tuple(self):
        return (self.symbol, self.open, self.high, self.low, self.close, self.volume, )

    def replace_with(self, bar):
        self.open = bar.open
        self.high = bar.high
        self.low = bar.low
        self.close = bar.close
        self.volume = bar.volume

    def aggregate(self, bar):
        self.high = max(self.high, bar.high)
        self.low = min(self.low, bar.low)
        self.close = bar.close
        self.volume += bar.volume

class BarWithTime:
    def epoch_seconds_to_datetime(timestamp_seconds):
        t = datetime.datetime.utcfromtimestamp(timestamp_seconds)
        t_tz = pytz.utc.localize(t)
        return t_tz

    def truncate_to_minute(timestamp_seconds):
        t_tz = BarWithTime.epoch_seconds_to_datetime(timestamp_seconds)
        t_tz_minute = t_tz.replace(second=0, microsecond=0)
        return t_tz_minute

    def __init__(self, time, bar):
        '''

        :param time: datetime instance in utc timezone
        :param bar:
        '''
        self.time = time
        self.bar = bar

    def __str__(self):
        return self.time.__str__() + ", " + self.bar.__str__()

    def get_next_bar_time(self):
        return self.time + datetime.timedelta(minutes=1)

    def truncate_time_minute(self):
        t = datetime.datetime.utcfromtimestamp(int(self.time.timestamp()))
        t_tz = pytz.utc.localize(t)
        t_tz_minute = t_tz.replace(second=0, microsecond=0)
        return t_tz_minute

    @staticmethod
    def get_minute_tuple_names():
        return ('datetime',) + Bar.get_tuple_names()

    @staticmethod
    def get_daily_tuple_names():
        return ('date',) + Bar.get_tuple_names()

    def to_tuple(self):
        return (self.time,) + self.bar.to_tuple()

    def to_tuple_with_epoch_seconds(self):
        return (int(self.time.timestamp()),) + self.bar.to_tuple()

    def replace_with(self, bar_with_time):
        self.bar.replace_with(bar_with_time.bar)

    def aggregate(self, bar_with_time):
        self.bar.aggregate(bar_with_time.bar)

class Aggregation:
    def __init__(self, symbol, bar_with_time_combine_mode = BAR_WITH_TIME_COMBINE_MODE.AGGREGATE, bar_with_times_max_length = _BAR_WITH_TIMES_MAX_LENGTH):
        self.symbol = symbol
        self.bar_with_times = deque()
        self.bar_with_times_max_length = bar_with_times_max_length
        self.t_now_tz = None
        self.bar_with_time_combine_mode = bar_with_time_combine_mode

    def set_bar_with_times_max_length(self, bar_with_times_max_length):
        self.bar_with_times_max_length = max(self.bar_with_times_max_length, bar_with_times_max_length)

    def _get_value_lists(self, column_names, query_range_minutes, drop_last = True):
        '''
        Gets the values list.

        :param column_names: a list of column names
        :param query_range_minutes: e.g. if this is 10 minutes, it gets the change up down to past 10 minutes from now.
        :return:
        '''
        res = {column: [] for column in column_names}
        l = len(self.bar_with_times)
        result_l = l - (1 if drop_last else 0)
        # for bwt in self.bar_with_times[-(query_range_minutes):]:
        for i in range(l - query_range_minutes, result_l):
            if i < 0: continue
            bwt = self.bar_with_times[i]
            for column in column_names:
                val = None
                if column == 'open':
                    val = bwt.bar.open
                elif column == 'high':
                    val = bwt.bar.high
                elif column == 'low':
                    val = bwt.bar.low
                elif column == 'close':
                    val = bwt.bar.close
                elif column == 'volume':
                    val = bwt.bar.volume
                res[column].append(val)
        return res

    def _get_quantity_list(self, query_range_minutes, drop_last = True):
        '''
        Gets the close * volume DataFrame, whose column name is "quantity".

        :param query_range_minutes: e.g. if this is 10 minutes, it gets the change up down to past 10 minutes from now.
        :return:
        '''
        value_lists = self._get_value_lists(['close', 'volume'], query_range_minutes, drop_last = drop_last)
        res = []
        l = len(value_lists['close'])
        if len(value_lists['volume']) != l:
            print('volume and close have different length in lists, something is wrong.')
        for i in range(l):
            res.append(value_lists['close'][i] * value_lists['volume'][i])
        return res

    def get_num_minutes_with_volume(self, query_range_minutes, threshold, drop_last=False):
        '''
        Gets the number of the minutes within the given range that have the volume larger than the threshold.

        :param query_range_minutes:
        :param threshold:
        :return:
        '''
        q_list = self._get_quantity_list(query_range_minutes, drop_last = drop_last)
        return np.sum(np.array(q_list) > threshold)

    def get_cumulative_quantity(self, query_range_minutes, drop_last=False):
        '''
        Gets the accumulative quantity (close * volume) value.

        :param numpy.float64 value.
        :return:
        '''
        q_list = self._get_quantity_list(query_range_minutes, drop_last = drop_last)
        return np.sum(q_list) if q_list else 0

    def get_minimal_quantity(self, query_range_minutes, drop_last=False):
        '''
        Gets the minimal quantity (close * volume) value within the given range.

        :param numpy.float64 value.
        :return:
        '''
        q_list = self._get_quantity_list(query_range_minutes, drop_last = drop_last)
        return np.min(q_list) if q_list else 0

    def get_avg_quantity(self, query_range_minutes, drop_last=False):
        '''
        Gets the minimal quantity (close * volume) value within the given range.

        :param numpy.float64 value.
        :return:
        '''
        q_list = self._get_quantity_list(query_range_minutes, drop_last = drop_last)
        return np.mean(q_list) if q_list else 0

    def _get_close_price(self):
        '''
        get the latest close price.

        :return: a value of numpy.float32 type
        '''
        if not len(self.bar_with_times):
            return 0
        bar_with_time = self.bar_with_times[-1]
        return bar_with_time.bar.close

    def get_close_price(self):
        return self._get_close_price()

    def _get_max_high_price(self, time_window_minutes):
        res = 0
        for bwt in list(self.bar_with_times)[-time_window_minutes:]:
            if bwt.bar.close > res:
                res = bwt.bar.high
        return res

    def _get_min_low_price(self, time_window_minutes):
        if not len(self.bar_with_times):
            return 0
        res = None
        for bwt in list(self.bar_with_times)[-time_window_minutes:]:
            if res is None or bwt.bar.close < res:
                res = bwt.bar.low
        return res

    def get_latest_time(self):
        if not len(self.bar_with_times):
            return None
        bar_with_time = self.bar_with_times[-1]
        return bar_with_time.time

    def set_now_tz(self, now_tz):
        self.t_now_tz = now_tz

    def _get_t_now_tz(self):
        if self.t_now_tz:
            return self.t_now_tz
        t_now = datetime.datetime.utcnow()
        return pytz.utc.localize(t_now)

    def _on_first_trade(self, trade):
        assert self.symbol == trade.symbol
        bar_timestamped = BarWithTime(BarWithTime.truncate_to_minute(trade.timestamp_seconds), Bar.new_bar_with_trade(trade.symbol, trade.price, 0))
        self.bar_with_times.append(bar_timestamped)
        self._on_append_new_bar_with_time()

    def _on_first_bar_with_time(self, bar_with_time):
        assert self.symbol == bar_with_time.bar.symbol
        bar_timestamped = BarWithTime(bar_with_time.truncate_time_minute(), bar_with_time.bar)
        self.bar_with_times.append(bar_timestamped)
        self._on_append_new_bar_with_time()

    def _new_bar_with_zero_volume(self, t, price):
        bar_timestamped = BarWithTime(t, Bar.new_bar_with_trade(self.symbol, price, 0))
        self.bar_with_times.append(bar_timestamped)
        self._on_append_new_bar_with_time()

    def _on_append_new_bar_with_time(self):
        while len(self.bar_with_times) > self.bar_with_times_max_length:
            self.bar_with_times.popleft()

    def on_trade(self, trade):
        assert self.symbol == trade.symbol
        if not self.bar_with_times:
            self._on_first_trade(trade)

        trade_t = BarWithTime.truncate_to_minute(trade.timestamp_seconds)
        cnt = 0 # for debug
        while True:
            bar_with_time = self.bar_with_times[-1]
            if bar_with_time.time >= trade_t:
                break

            time = bar_with_time.get_next_bar_time()
            price = bar_with_time.bar.close
            if time == trade_t:
                price = trade.price
            self._new_bar_with_zero_volume(time, price)
            cnt += 1
            #print('cnt: {c}, trade_t: {tt}, bar time: {bt}'.format(c=cnt, tt=str(trade_t), bt=str(bar_with_time.time)))

        bar_with_time = self.bar_with_times[-1]
        assert bar_with_time.time >= trade_t
        bar_with_time.bar.on_trade(trade)

    def on_bar_with_time(self, new_bar_with_time):
        assert self.symbol == new_bar_with_time.bar.symbol
        if not self.bar_with_times:
            self._on_first_bar_with_time(new_bar_with_time)
            return

        new_bar_t = new_bar_with_time.truncate_time_minute()
        cnt = 0
        while True:
            l = len(self.bar_with_times)
            cnt += 1
            if cnt > 100:
                print('breaking after more than {cnt} loops for {s}, new_bar_with_time: {new_bar_with_time}'.format(cnt=cnt, s=self.symbol, new_bar_with_time=new_bar_with_time))
                break
            bar_with_time = self.bar_with_times[-1]
            if new_bar_t < bar_with_time.time:
                recent_bars_str = [str(b) for b in list(self.bar_with_times)[-5:]]
                logging.info('bar_t is lesser than last bar time. cnt: {cnt} loops, new bar: {nb}, self.bar_w_ts.length: {l}, last bar: {lb}, latest bars: {bars}'.format(
                    cnt=cnt, nb=new_bar_with_time, l=l, lb= self.bar_with_times[-1] if l > 0 else 'none', bars=recent_bars_str))
                break
            #print('bar_t is not lesser than the last', new_bar_with_time, self.bar_with_times[-1])
            if new_bar_t == bar_with_time.time:
                if self.bar_with_time_combine_mode is BAR_WITH_TIME_COMBINE_MODE.REPLACE:
                    bar_with_time.replace_with(new_bar_with_time)
                elif self.bar_with_time_combine_mode is BAR_WITH_TIME_COMBINE_MODE.AGGREGATE:
                    bar_with_time.aggregate(new_bar_with_time)
                break

            onestep_time = bar_with_time.get_next_bar_time()
            price = bar_with_time.bar.close
            if onestep_time == new_bar_t:
                price = new_bar_with_time.bar.open
            #print('new bar at time', onestep_time, 'price', price)
            self._new_bar_with_zero_volume(onestep_time, price)

        if len(self.bar_with_times) == 0:
            print('bar_with_times has no elements')

    def get_minute_df(self, range_minutes = None, print_log = True):
        if print_log:
            print('Aggregation.get_minute_df for {symbol}, {l} total bars, range_minutes: {range_minutes}'.format(
                symbol=self.symbol, l=len(self.bar_with_times), range_minutes=range_minutes if range_minutes else 'all'))
        tuples = list(map(lambda b: b.to_tuple(), self.bar_with_times))
        if range_minutes:
            t_now_tz = self._get_t_now_tz()
            i = len(tuples)
            while True:
                if i == 0:
                    break
                else:
                    dt = t_now_tz - tuples[i - 1][0]
                    if dt.seconds / 60 >= range_minutes:
                        break
                i -= 1
            tuples = tuples[i:]
        return pd.DataFrame(tuples, columns = BarWithTime.get_minute_tuple_names())

