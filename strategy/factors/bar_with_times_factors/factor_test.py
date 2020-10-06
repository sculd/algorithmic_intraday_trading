import unittest, datetime
import util.time as time_util
from ingest.streaming.aggregation import BarWithTime, Bar
import pytz

from strategy.factors.bar_with_times_factors.factor import BarWithTimesFactor

def _make_bar_with_times(minute, symbol, price):
    return BarWithTime(BarWithTime.truncate_to_minute(minute), Bar(symbol, price, price, price, price, 1))

class TestFactor(unittest.TestCase):
    def test_get_change(self):
        symbol = 'DUMMY_SYMBOL'
        bar_with_times = []
        bar_with_times.append(_make_bar_with_times(1, symbol, 110))
        bar_with_times.append(_make_bar_with_times(2, symbol, 120))
        bar_with_times.append(_make_bar_with_times(3, symbol, 130))
        bar_with_times.append(_make_bar_with_times(4, symbol, 140))
        signal = BarWithTimesFactor(symbol, bar_with_times)

        chage_list = signal.get_change_list('close', 2, 1)
        self.assertEqual(1, len(chage_list))
        self.assertEqual((140.0-120)/120, chage_list[0])

        chage_list = signal.get_change_list('close', 2, 2)
        self.assertEqual(2, len(chage_list))
        self.assertEqual((130.0-110)/110, chage_list[0])
        self.assertEqual((140.0-120)/120, chage_list[1])

    def test_get_change_list_overflow(self):
        symbol = 'DUMMY_SYMBOL'
        bar_with_times = []
        bar_with_times.append(_make_bar_with_times(0, symbol, 100))
        bar_with_times.append(_make_bar_with_times(1, symbol, 110))
        signal = BarWithTimesFactor(symbol, bar_with_times)

        chage_list = signal.get_change_list('close', 10, 1)
        self.assertEqual(1, len(chage_list))
        self.assertEqual(0, chage_list[0])

    def test_get_max_amplitude_change_trivial(self):
        symbol = 'DUMMY_SYMBOL'
        bar_with_times = []
        bar_with_times.append(_make_bar_with_times(0, symbol, 100))
        bar_with_times.append(_make_bar_with_times(1, symbol, 110))
        bar_with_times.append(_make_bar_with_times(2, symbol, 120))
        bar_with_times.append(_make_bar_with_times(3, symbol, 130))
        bar_with_times.append(_make_bar_with_times(4, symbol, 140))
        signal = BarWithTimesFactor(symbol, bar_with_times)
        ch = signal.get_max_amplitude_change('close', 4)
        self.assertEqual(40.0 / 100, ch)

    def test_get_max_amplitude_change_drop_jump(self):
        symbol = 'DUMMY_SYMBOL'
        bar_with_times = []
        bar_with_times.append(_make_bar_with_times(0, symbol, 100))
        bar_with_times.append(_make_bar_with_times(1, symbol, 50))
        bar_with_times.append(_make_bar_with_times(2, symbol, 120))
        bar_with_times.append(_make_bar_with_times(3, symbol, 130))
        bar_with_times.append(_make_bar_with_times(4, symbol, 140))
        signal = BarWithTimesFactor(symbol, bar_with_times)
        ch = signal.get_max_amplitude_change('close', 4)
        self.assertEqual((140 - 50) / 50, ch)

    def test_get_max_amplitude_change_jump_drop(self):
        symbol = 'DUMMY_SYMBOL'
        bar_with_times = []
        bar_with_times.append(_make_bar_with_times(0, symbol, 100))
        bar_with_times.append(_make_bar_with_times(1, symbol, 150))
        bar_with_times.append(_make_bar_with_times(2, symbol, 90))
        bar_with_times.append(_make_bar_with_times(3, symbol, 80))
        bar_with_times.append(_make_bar_with_times(4, symbol, 70))
        signal = BarWithTimesFactor(symbol, bar_with_times)
        ch = signal.get_max_amplitude_change('close', 4)
        self.assertEqual((70 - 150) / 150, ch)

    def test_get_max_amplitude_change_too_early_drop_jump(self):
        symbol = 'DUMMY_SYMBOL'
        bar_with_times = []
        bar_with_times.append(_make_bar_with_times(0, symbol, 100))
        bar_with_times.append(_make_bar_with_times(1, symbol, 50))
        bar_with_times.append(_make_bar_with_times(2, symbol, 120))
        bar_with_times.append(_make_bar_with_times(3, symbol, 130))
        bar_with_times.append(_make_bar_with_times(4, symbol, 140))
        bar_with_times.append(_make_bar_with_times(5, symbol, 150))
        bar_with_times.append(_make_bar_with_times(6, symbol, 160))
        signal = BarWithTimesFactor(symbol, bar_with_times)
        ch = signal.get_max_amplitude_change('close', 4)
        self.assertEqual((160 - 120) / 120.0, ch)
