import unittest, datetime
import util.time as time_util
import pytz

from ingest.streaming import TimeseriesValue, TimeseriesValueWithTime, Timeseries

class TestTimeseriesValue(unittest.TestCase):
    def test_new_timeseries_value(self):
        symbol = 'DUMMY_SYMBOL'
        ts_value = TimeseriesValue(symbol, 'close', 100)
        self.assertEqual(symbol, ts_value.symbol)
        self.assertEqual('close', ts_value.value_name)
        self.assertEqual(100, ts_value.value)

    def test_get_tuple_names(self):
        symbol = 'DUMMY_SYMBOL'
        ts_value = TimeseriesValue(symbol, 'close', 100)
        self.assertEqual(('symbol', 'close', ), ts_value.get_tuple_names())

    def test_get_tuple(self):
        symbol = 'DUMMY_SYMBOL'
        ts_value = TimeseriesValue(symbol, 'close', 100)
        self.assertEqual(('DUMMY_SYMBOL', 100, ), ts_value.to_tuple())

class TestTimeseriesValueWithTime(unittest.TestCase):
    def test_to_tuple(self):
        symbol = 'DUMMY_SYMBOL'
        ts_value = TimeseriesValue(symbol, 'close', 100)
        ts_value_with_time = TimeseriesValueWithTime(time_util.truncate_utc_timestamp_to_minute(0), ts_value)
        t_want = datetime.datetime.utcfromtimestamp(0)
        t_tz_want = pytz.utc.localize(t_want)
        self.assertEqual((t_tz_want, 'DUMMY_SYMBOL', 100, ), ts_value_with_time.to_tuple())

    def test_get_minute_tuple_names(self):
        symbol = 'DUMMY_SYMBOL'
        ts_value = TimeseriesValue(symbol, 'close', 100)
        ts_value_with_time = TimeseriesValueWithTime(time_util.truncate_utc_timestamp_to_minute(0), ts_value)
        self.assertEqual(('datetime', 'symbol', 'close', ), ts_value_with_time.get_minute_tuple_names())

class TestTimeseries(unittest.TestCase):
    def test_get_change(self):
        symbol = 'DUMMY_SYMBOL'
        def tuple_to_tsvalue_with_time(pair):
            return TimeseriesValueWithTime(time_util.truncate_utc_timestamp_to_minute(60 * pair[0]), TimeseriesValue(symbol, 'close', pair[1]))
        ts_value_with_time = list(map(lambda t_v: tuple_to_tsvalue_with_time(t_v), [(0, 100), (1, 110), (4, 140), (5, 150)]))
        ts = Timeseries(symbol, 'close', ts_value_with_time)
        ts._set_now_tz(pytz.utc.localize(datetime.datetime.utcfromtimestamp(60 * 5)))

        ts_change_5_0_got = ts.get_change(5, 0)
        self.assertEqual(symbol, ts_change_5_0_got.symbol)
        self.assertEqual('close', ts_change_5_0_got.value_name)
        self.assertEqual(1, len(ts_change_5_0_got.timeseries_value_with_time))
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 5), ts_change_5_0_got.timeseries_value_with_time[0].time)
        self.assertEqual(symbol, ts_change_5_0_got.timeseries_value_with_time[0].timeseries_value.symbol)
        self.assertEqual('close', ts_change_5_0_got.timeseries_value_with_time[0].timeseries_value.value_name)
        self.assertEqual(0.5, ts_change_5_0_got.timeseries_value_with_time[0].timeseries_value.value)

        ts_change_5_1_got = ts.get_change(5, 1)
        self.assertEqual(2, len(ts_change_5_1_got.timeseries_value_with_time))
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 4), ts_change_5_1_got.timeseries_value_with_time[0].time)
        self.assertEqual(0.4, ts_change_5_1_got.timeseries_value_with_time[0].timeseries_value.value)
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 5), ts_change_5_1_got.timeseries_value_with_time[1].time)
        self.assertEqual(0.5, ts_change_5_1_got.timeseries_value_with_time[1].timeseries_value.value)

        ts_change_5_2_got = ts.get_change(5, 2)
        self.assertEqual(2, len(ts_change_5_2_got.timeseries_value_with_time))
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 4), ts_change_5_2_got.timeseries_value_with_time[0].time)
        self.assertEqual(0.4, ts_change_5_2_got.timeseries_value_with_time[0].timeseries_value.value)
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 5), ts_change_5_2_got.timeseries_value_with_time[1].time)
        self.assertEqual(0.5, ts_change_5_2_got.timeseries_value_with_time[1].timeseries_value.value)

        ts_change_5_4_got = ts.get_change(5, 4)
        self.assertEqual(3, len(ts_change_5_4_got.timeseries_value_with_time))
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 1), ts_change_5_4_got.timeseries_value_with_time[0].time)
        self.assertEqual(0.1, ts_change_5_4_got.timeseries_value_with_time[0].timeseries_value.value)
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 4), ts_change_5_4_got.timeseries_value_with_time[1].time)
        self.assertEqual(0.4, ts_change_5_4_got.timeseries_value_with_time[1].timeseries_value.value)
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 5), ts_change_5_4_got.timeseries_value_with_time[2].time)
        self.assertEqual(0.5, ts_change_5_4_got.timeseries_value_with_time[2].timeseries_value.value)

        ts_change_1_1_got = ts.get_change(1, 1)
        self.assertEqual(2, len(ts_change_1_1_got.timeseries_value_with_time))
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 4), ts_change_1_1_got.timeseries_value_with_time[0].time)
        self.assertEqual(0.0, ts_change_1_1_got.timeseries_value_with_time[0].timeseries_value.value)
        self.assertEqual(time_util.truncate_utc_timestamp_to_minute(60 * 5), ts_change_1_1_got.timeseries_value_with_time[1].time)
        self.assertEqual(10.0/140, ts_change_1_1_got.timeseries_value_with_time[1].timeseries_value.value)

