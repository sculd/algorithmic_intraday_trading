import unittest, datetime
import pytz

from ingest.streaming.aggregation import Aggregation, BarWithTime, Bar, Trade
from strategy.factors.bar_with_times_factors.sudden_move import SuddenMove, SuddenMoveParameter, PRICE_MOVE_MODE

class TestAggregation(unittest.TestCase):
    def test_get_market_signal(self):
        symbol = 'DUMMY_SYMBOL'
        one_minute_seconds = 60
        time_0 = BarWithTime.truncate_to_minute(0)
        time_6 = datetime.datetime.fromtimestamp(one_minute_seconds * 6)
        time_61 = datetime.datetime.fromtimestamp(one_minute_seconds * 6 + 1)
        time_62 = datetime.datetime.fromtimestamp(one_minute_seconds * 6 + 2)
        aggregation = Aggregation(symbol)
        factor_param = SuddenMoveParameter(0.1, -0.1, 1.0, 0.1, 5, 3)
        sudde_move = SuddenMove(symbol, aggregation, factor_param)

        aggregation.on_bar_with_time(BarWithTime(time_0, Bar(symbol, 100, 100, 100, 100, 1.0)))
        aggregation.on_bar_with_time(BarWithTime(time_6, Bar(symbol, 109, 109, 109, 109, 1.0)))
        aggregation.on_bar_with_time(BarWithTime(time_61, Bar(symbol, 109, 109, 109, 109, 1.0)))
        self.assertEqual(sudde_move.get_market_signal(), PRICE_MOVE_MODE.NO_SIGNAL)

        aggregation.on_bar_with_time(BarWithTime(time_62, Bar(symbol, 111, 111, 111, 111, 1.0)))
        self.assertTrue(sudde_move.get_market_signal(), PRICE_MOVE_MODE.JUMP_SIGNAL)


