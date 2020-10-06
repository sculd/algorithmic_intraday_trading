import unittest, datetime
from ingest.streaming.orderbook import Orderbook, OrderbookSnapshot
import pytz

from strategy.factors.orderbook_factors.average_trade_price import AverageTradePrice, AverageTradePriceParameter

class TestFactor(unittest.TestCase):
    def test_get(self):
        symbol = 'DUMMY_SYMBOL'
        orderbook = Orderbook(symbol)
        param = AverageTradePriceParameter()
        factor = AverageTradePrice(symbol, orderbook, param)

        snapshot1 = OrderbookSnapshot(symbol)
        snapshot1.bid_prices.append(100)
        snapshot1.bid_sizes.append(10)
        snapshot1.ask_prices.append(110)
        snapshot1.ask_sizes.append(12)
        snapshot1.last_size = 5
        snapshot1.last_price = 110
        snapshot1.epoch_seconds = 0
        orderbook.on_update(snapshot1)

        got = factor.get()
        want = 105.0  # avg of 100, 110
        self.assertEqual(want, got)

        snapshot2 = OrderbookSnapshot(symbol)
        snapshot2.bid_prices.append(101)
        snapshot2.bid_sizes.append(11)
        snapshot2.ask_prices.append(109)
        snapshot2.ask_sizes.append(14)
        snapshot2.last_size = 10
        snapshot2.last_price = 109
        snapshot2.epoch_seconds = 60
        orderbook.on_update(snapshot2)

        got = factor.get()
        want = -0.2  # (109 - 110) / (10 - 5)
        self.assertEqual(want, got)

        got = factor.get()
        want = -0.2  # no change
        self.assertEqual(want, got)

        snapshot2 = OrderbookSnapshot(symbol)
        snapshot2.bid_prices.append(101)
        snapshot2.bid_sizes.append(11)
        snapshot2.ask_prices.append(109)
        snapshot2.ask_sizes.append(14)
        snapshot2.last_size = 10
        snapshot2.last_price = 119
        snapshot2.epoch_seconds = 60
        orderbook.on_update(snapshot2)

        got = factor.get()
        want = -0.2  # same volume
        self.assertEqual(want, got)
