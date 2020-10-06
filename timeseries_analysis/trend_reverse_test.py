import unittest, datetime
import pytz
import timeseries_analysis.trend_reverse
from util.current_time import MockCurrentTime

from ingest.streaming.aggregation import Aggregation, BarWithTime, Bar, Trade

class TestBar(unittest.TestCase):
    symbol = 'DUMMYSYM'
    def _bar(price):
        return Bar(TestBar.symbol, price, price, price, price, 1.0)

    def test_short(self):
        param = timeseries_analysis.trend_reverse.Param(
            datetime.timedelta(minutes=60),
            0.3,
            -0.3,
            datetime.timedelta(minutes=10),
            -0.1,
            0.1
        )

        aggregation = Aggregation(TestBar.symbol)
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 0), TestBar._bar(100)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 1), TestBar._bar(110)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 61), TestBar._bar(150)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 65), TestBar._bar(120)))

        current_time = MockCurrentTime(60 * 65)
        analyze = timeseries_analysis.trend_reverse.Analyze(aggregation, param, current_time=current_time)
        self.assertEqual(timeseries_analysis.trend_reverse.POSITION_MODE.SHORT, analyze.analyze())

    def test_long(self):
        param = timeseries_analysis.trend_reverse.Param(
            datetime.timedelta(minutes=60),
            0.3,
            -0.3,
            datetime.timedelta(minutes=10),
            -0.1,
            0.1
        )

        aggregation = Aggregation(TestBar.symbol)
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 0), TestBar._bar(100)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 1), TestBar._bar(90)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 61), TestBar._bar(40)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 65), TestBar._bar(60)))

        current_time = MockCurrentTime(60 * 65)
        analyze = timeseries_analysis.trend_reverse.Analyze(aggregation, param, current_time=current_time)
        self.assertEqual(timeseries_analysis.trend_reverse.POSITION_MODE.LONG, analyze.analyze())

    def test_outside_reversal_change_widow_size(self):
        param = timeseries_analysis.trend_reverse.Param(
            datetime.timedelta(minutes=60),
            0.3,
            -0.3,
            datetime.timedelta(minutes=10),
            -0.1,
            0.1
        )

        aggregation = Aggregation(TestBar.symbol)
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 0), TestBar._bar(100)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 1), TestBar._bar(90)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 61), TestBar._bar(40)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 65), TestBar._bar(60)))

        current_time = MockCurrentTime(60 * 78)
        analyze = timeseries_analysis.trend_reverse.Analyze(aggregation, param, current_time=current_time)
        self.assertEqual(timeseries_analysis.trend_reverse.POSITION_MODE.NO_POSITION, analyze.analyze())

    def test_outside_reversal_not_large_enough(self):
        param = timeseries_analysis.trend_reverse.Param(
            datetime.timedelta(minutes=60),
            0.3,
            -0.3,
            datetime.timedelta(minutes=10),
            -0.1,
            0.1
        )

        aggregation = Aggregation(TestBar.symbol)
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 0), TestBar._bar(100)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 1), TestBar._bar(90)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 61), TestBar._bar(40)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 65), TestBar._bar(42)))

        current_time = MockCurrentTime(60 * 65)
        analyze = timeseries_analysis.trend_reverse.Analyze(aggregation, param, current_time=current_time)
        self.assertEqual(timeseries_analysis.trend_reverse.POSITION_MODE.NO_POSITION, analyze.analyze())

    def test_outside_no_reversal_yet(self):
        param = timeseries_analysis.trend_reverse.Param(
            datetime.timedelta(minutes=60),
            0.3,
            -0.3,
            datetime.timedelta(minutes=10),
            -0.1,
            0.1
        )

        aggregation = Aggregation(TestBar.symbol)
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 0), TestBar._bar(100)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 1), TestBar._bar(90)))
        aggregation.on_bar_with_time(BarWithTime(BarWithTime.truncate_to_minute(60 * 61), TestBar._bar(40)))

        current_time = MockCurrentTime(60 * 62)
        analyze = timeseries_analysis.trend_reverse.Analyze(aggregation, param, current_time=current_time)
        self.assertEqual(timeseries_analysis.trend_reverse.POSITION_MODE.NO_POSITION, analyze.analyze())
