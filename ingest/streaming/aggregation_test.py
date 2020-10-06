import unittest, datetime
import pytz

from ingest.streaming.aggregation import Aggregation, BarWithTime, Bar, Trade

class TestBar(unittest.TestCase):
    def test_bar_on_trade(self):
        symbol = 'DUMMY_SYMBOL'
        bar = Bar.new_bar_with_trade(symbol, 100, 1.0)
        self.assertEqual(100, bar.open)
        self.assertEqual(100, bar.high)
        self.assertEqual(100, bar.low)
        self.assertEqual(100, bar.close)
        self.assertEqual(1, bar.volume)

        bar.on_trade(Trade(0, symbol, 110.0, 1.0))
        self.assertEqual(100, bar.open)
        self.assertEqual(110, bar.high)
        self.assertEqual(100, bar.low)
        self.assertEqual(110, bar.close)
        self.assertEqual(2, bar.volume)

        bar.on_trade(Trade(0, symbol, 90.0, 1.0))
        self.assertEqual(100, bar.open)
        self.assertEqual(110, bar.high)
        self.assertEqual(90, bar.low)
        self.assertEqual(90, bar.close)
        self.assertEqual(3, bar.volume)

class TestAggregation(unittest.TestCase):
    def test_on_trade(self):
        one_minute_seconds = 60
        symbol = 'DUMMY_SYMBOL'
        aggregation = Aggregation(symbol)
        aggregation.on_trade(Trade(0, symbol, 100.0, 1.0))
        aggregation.on_trade(Trade(1, symbol, 90.0, 1.0))
        aggregation.on_trade(Trade(2, symbol, 100.0, 1.0))
        aggregation.on_trade(Trade(3, symbol, 120.0, 1.0))
        aggregation.on_trade(Trade(4, symbol, 110.0, 1.0))

        aggregation.on_trade(Trade(one_minute_seconds, symbol, 110.0, 1.0))
        # skip minute 2
        aggregation.on_trade(Trade(one_minute_seconds * 3 + 1, symbol, 120.0, 1.0))
        aggregation.on_trade(Trade(one_minute_seconds * 3 + 2, symbol, 90.0, 1.0))

        self.assertEqual(4, len(aggregation.bar_with_times))

        bar_t_0 = aggregation.bar_with_times[0]
        self.assertEqual(bar_t_0.time.timestamp(), 0)
        self.assertEqual(symbol, bar_t_0.bar.symbol)
        self.assertEqual(100, bar_t_0.bar.open)
        self.assertEqual(120, bar_t_0.bar.high)
        self.assertEqual(90, bar_t_0.bar.low)
        self.assertEqual(110, bar_t_0.bar.close)
        self.assertEqual(5, bar_t_0.bar.volume)

        bar_t_1 = aggregation.bar_with_times[1]
        self.assertEqual(bar_t_1.time.timestamp(), one_minute_seconds)
        self.assertEqual(symbol, bar_t_1.bar.symbol)
        self.assertEqual(110, bar_t_1.bar.open)
        self.assertEqual(110, bar_t_1.bar.high)
        self.assertEqual(110, bar_t_1.bar.low)
        self.assertEqual(110, bar_t_1.bar.close)
        self.assertEqual(1, bar_t_1.bar.volume)

        bar_t_2 = aggregation.bar_with_times[2]
        self.assertEqual(bar_t_2.time.timestamp(), one_minute_seconds * 2)
        self.assertEqual(symbol, bar_t_2.bar.symbol)
        self.assertEqual(110, bar_t_2.bar.open)
        self.assertEqual(110, bar_t_2.bar.high)
        self.assertEqual(110, bar_t_2.bar.low)
        self.assertEqual(110, bar_t_2.bar.close)
        self.assertEqual(0, bar_t_2.bar.volume)

        bar_t_3 = aggregation.bar_with_times[3]
        self.assertEqual(bar_t_3.time.timestamp(), one_minute_seconds * 3)
        self.assertEqual(symbol, bar_t_3.bar.symbol)
        self.assertEqual(120, bar_t_3.bar.open)
        self.assertEqual(120, bar_t_3.bar.high)
        self.assertEqual(90, bar_t_3.bar.low)
        self.assertEqual(90, bar_t_3.bar.close)
        self.assertEqual(2, bar_t_3.bar.volume)

    def test_on_bar_with_time(self):
        symbol = 'DUMMY_SYMBOL'
        one_minute_seconds = 60
        time_0 = BarWithTime.truncate_to_minute(0)
        time_2 = BarWithTime.truncate_to_minute(one_minute_seconds * 2)

        aggregation = Aggregation(symbol)

        aggregation.on_bar_with_time(BarWithTime(time_0, Bar(symbol, 100, 110, 90, 110, 1.0)))

        # skip minute 1

        aggregation.on_bar_with_time(BarWithTime(time_2, Bar(symbol, 110, 130, 100, 130, 3.0)))

        self.assertEqual(3, len(aggregation.bar_with_times))

        bar_t_0 = aggregation.bar_with_times[0]
        self.assertEqual(bar_t_0.time.timestamp(), 0)
        self.assertEqual(symbol, bar_t_0.bar.symbol)
        self.assertEqual(100, bar_t_0.bar.open)
        self.assertEqual(110, bar_t_0.bar.high)
        self.assertEqual(90, bar_t_0.bar.low)
        self.assertEqual(110, bar_t_0.bar.close)
        self.assertEqual(1, bar_t_0.bar.volume)

        bar_t_1 = aggregation.bar_with_times[1]
        self.assertEqual(bar_t_1.time.timestamp(), one_minute_seconds)
        self.assertEqual(symbol, bar_t_1.bar.symbol)
        self.assertEqual(110, bar_t_1.bar.open)
        self.assertEqual(110, bar_t_1.bar.high)
        self.assertEqual(110, bar_t_1.bar.low)
        self.assertEqual(110, bar_t_1.bar.close)
        self.assertEqual(0, bar_t_1.bar.volume)

        bar_t_2 = aggregation.bar_with_times[2]
        self.assertEqual(bar_t_2.time.timestamp(), one_minute_seconds * 2)
        self.assertEqual(symbol, bar_t_2.bar.symbol)
        self.assertEqual(110, bar_t_2.bar.open)
        self.assertEqual(130, bar_t_2.bar.high)
        self.assertEqual(100, bar_t_2.bar.low)
        self.assertEqual(130, bar_t_2.bar.close)
        self.assertEqual(3.0, bar_t_2.bar.volume)

    def test_on_bar_with_time_by_second(self):
        symbol = 'DUMMY_SYMBOL'
        one_minute_seconds = 60
        time_0 = BarWithTime.truncate_to_minute(0)
        time01 = time_0 + datetime.timedelta(seconds=1)
        time1 = datetime.datetime.fromtimestamp(one_minute_seconds * 1)
        aggregation = Aggregation(symbol)

        aggregation.on_bar_with_time(BarWithTime(time_0, Bar(symbol, 100, 110, 90, 110, 1.0)))
        aggregation.on_bar_with_time(BarWithTime(time01, Bar(symbol, 110, 120, 100, 115, 1.0)))

        aggregation.on_bar_with_time(BarWithTime(time1, Bar(symbol, 115, 130, 110, 130, 5.0)))

        self.assertEqual(2, len(aggregation.bar_with_times))

        bar_t_0 = aggregation.bar_with_times[0]
        self.assertEqual(bar_t_0.time.timestamp(), 0)
        self.assertEqual(symbol, bar_t_0.bar.symbol)
        self.assertEqual(100, bar_t_0.bar.open)
        self.assertEqual(120, bar_t_0.bar.high)
        self.assertEqual(90, bar_t_0.bar.low)
        self.assertEqual(115, bar_t_0.bar.close)
        self.assertEqual(2, bar_t_0.bar.volume)

        bar_t_1 = aggregation.bar_with_times[1]
        self.assertEqual(bar_t_1.time.timestamp(), one_minute_seconds)
        self.assertEqual(symbol, bar_t_1.bar.symbol)
        self.assertEqual(115, bar_t_1.bar.open)
        self.assertEqual(130, bar_t_1.bar.high)
        self.assertEqual(110, bar_t_1.bar.low)
        self.assertEqual(130, bar_t_1.bar.close)
        self.assertEqual(5, bar_t_1.bar.volume)

    def test_minute_df(self):
        one_minute_seconds = 60
        symbol = 'DUMMY_SYMBOL'
        aggregation = Aggregation(symbol)
        aggregation.bar_with_times.append(BarWithTime(BarWithTime.truncate_to_minute(0), Bar(symbol, 100, 120, 90, 110, 3)))
        aggregation.bar_with_times.append(BarWithTime(BarWithTime.truncate_to_minute(one_minute_seconds), Bar(symbol, 110, 130, 80, 130, 1)))
        df = aggregation.get_minute_df()
        self.assertEqual(2, len(df))
        row_0 = df.iloc[0]
        self.assertEqual(100, row_0.open)
        self.assertEqual(120, row_0.high)
        self.assertEqual(90, row_0.low)
        self.assertEqual(110, row_0.close)
        self.assertEqual(3, row_0.volume)
        row_1 = df.iloc[1]
        self.assertEqual(110, row_1.open)
        self.assertEqual(130, row_1.high)
        self.assertEqual(80, row_1.low)
        self.assertEqual(130, row_1.close)
        self.assertEqual(1, row_1.volume)

    def test_minute_df_with_range_minutes(self):
        one_minute_seconds = 60
        symbol = 'DUMMY_SYMBOL'
        aggregation = Aggregation(symbol)
        aggregation.set_now_tz(pytz.utc.localize(datetime.datetime.utcfromtimestamp(one_minute_seconds * 2)))
        aggregation.bar_with_times.append(BarWithTime(BarWithTime.truncate_to_minute(0), Bar(symbol, 100, 110, 90, 100, 1)))
        aggregation.bar_with_times.append(BarWithTime(BarWithTime.truncate_to_minute(one_minute_seconds), Bar(symbol, 110, 120, 100, 110, 2)))
        aggregation.bar_with_times.append(BarWithTime(BarWithTime.truncate_to_minute(one_minute_seconds * 2), Bar(symbol, 120, 130, 110, 120, 3)))

        df_2m = aggregation.get_minute_df(range_minutes=2)
        self.assertEqual(2, len(df_2m))
        row_0_2m = df_2m.iloc[0]
        self.assertEqual(110, row_0_2m.open)
        self.assertEqual(120, row_0_2m.high)
        self.assertEqual(100, row_0_2m.low)
        self.assertEqual(110, row_0_2m.close)
        self.assertEqual(2, row_0_2m.volume)
        row_1_2m = df_2m.iloc[1]
        self.assertEqual(120, row_1_2m.open)
        self.assertEqual(130, row_1_2m.high)
        self.assertEqual(110, row_1_2m.low)
        self.assertEqual(120, row_1_2m.close)
        self.assertEqual(3, row_1_2m.volume)

        df_4m = aggregation.get_minute_df(range_minutes=4)
        self.assertEqual(3, len(df_4m))

    def test_get_quantity_list(self):
        symbol = 'DUMMY_SYMBOL'
        signal = Aggregation(symbol)
        signal.on_trade(Trade(0 * 60, symbol, 100.0, 1.0))
        # skip miniute 1
        signal.on_trade(Trade(2 * 60, symbol, 110.0, 2.0))

        q_list = signal._get_quantity_list(1, drop_last=False)
        self.assertEqual(1, len(q_list))
        self.assertEqual(220.0, q_list[0])

        q_list = signal._get_quantity_list(10, drop_last=False)
        self.assertEqual(3, len(q_list))
        self.assertEqual(100.0, q_list[0])
        self.assertEqual(0, q_list[1])
        self.assertEqual(220.0, q_list[2])

    def test_get_minimal_quantity(self):
        symbol = 'DUMMY_SYMBOL'
        signal = Aggregation(symbol)
        signal.on_trade(Trade(0 * 60, symbol, 100.0, 1.0))
        min_q = signal.get_minimal_quantity(10)
        self.assertEqual(100, min_q)

        # skip miniute 1
        signal.on_trade(Trade(2 * 60, symbol, 110.0, 2.0))
        min_q = signal.get_minimal_quantity(10)
        self.assertEqual(0, min_q)

    def test_get_cumulative_quantity(self):
        symbol = 'DUMMY_SYMBOL'
        signal = Aggregation(symbol)
        signal.on_trade(Trade(0 * 60, symbol, 100.0, 1.0))
        # skip miniute 1
        signal.on_trade(Trade(2 * 60, symbol, 110.0, 2.0))

        cq = signal.get_cumulative_quantity(5)
        self.assertEqual(320.0, cq)

    def test_get_value_lists(self):
        symbol = 'DUMMY_SYMBOL'
        signal = Aggregation(symbol)
        signal.on_trade(Trade(0 * 60, symbol, 100.0, 1.0))
        # skip minute 1
        signal.on_trade(Trade(2 * 60, symbol, 120.0, 1.0))
        signal.on_trade(Trade(3 * 60, symbol, 130.0, 1.0))
        signal.on_trade(Trade(4 * 60, symbol, 140.0, 1.0))

        v_list = signal._get_value_lists(['close'], 1, drop_last=False)
        self.assertEqual(1, len(v_list['close']))
        self.assertEqual(140.0, v_list['close'][0])

        v_list = signal._get_value_lists(['close'], 10, drop_last=False)
        self.assertEqual(5, len(v_list['close']))
        self.assertEqual(100.0, v_list['close'][0])
        self.assertEqual(140.0, v_list['close'][-1])

        v_list = signal._get_value_lists(['volume'], 1, drop_last=False)
        self.assertEqual(1, len(v_list['volume']))
        self.assertEqual(1.0, v_list['volume'][0])

        v_list = signal._get_value_lists(['volume'], 10, drop_last=False)
        self.assertEqual(5, len(v_list['volume']))
        self.assertEqual(1.0, v_list['volume'][0])
        self.assertEqual(1.0, v_list['volume'][-1])

