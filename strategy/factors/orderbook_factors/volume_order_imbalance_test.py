import unittest, datetime
from ingest.streaming.orderbook import Orderbook, OrderbookSnapshot
import pytz

from strategy.factors.orderbook_factors.volume_order_imbalance import VolumeOrderImbalance, VolumeOrderImbalanceParameter

class TestFactor(unittest.TestCase):
    def test_get_bid_p_change_ask_p_change(self):
        symbol = 'DUMMY_SYMBOL'
        orderbook = Orderbook(symbol)

        snapshot1 = OrderbookSnapshot(symbol)
        snapshot1.bid_prices.append(100)
        snapshot1.bid_sizes.append(10)
        snapshot1.ask_prices.append(110)
        snapshot1.ask_sizes.append(12)
        snapshot1.epoch_seconds = 0
        orderbook.on_update(snapshot1)

        snapshot2 = OrderbookSnapshot(symbol)
        snapshot2.bid_prices.append(101)
        snapshot2.bid_sizes.append(11)
        snapshot2.ask_prices.append(109)
        snapshot2.ask_sizes.append(14)
        snapshot2.epoch_seconds = 60
        orderbook.on_update(snapshot2)

        param = VolumeOrderImbalanceParameter()
        factor = VolumeOrderImbalance(symbol, orderbook, param)

        got = factor.get()
        want = -3  # 11 - 14
        self.assertEqual(want, got)

    def test_get_bid_p_change_ask_p_no_change(self):
        symbol = 'DUMMY_SYMBOL'
        orderbook = Orderbook(symbol)

        snapshot1 = OrderbookSnapshot(symbol)
        snapshot1.bid_prices.append(100)
        snapshot1.bid_sizes.append(10)
        snapshot1.ask_prices.append(110)
        snapshot1.ask_sizes.append(12)
        snapshot1.epoch_seconds = 0
        orderbook.on_update(snapshot1)

        snapshot2 = OrderbookSnapshot(symbol)
        snapshot2.bid_prices.append(101)
        snapshot2.bid_sizes.append(11)
        snapshot2.ask_prices.append(110)
        snapshot2.ask_sizes.append(14)
        snapshot2.epoch_seconds = 60
        orderbook.on_update(snapshot2)

        param = VolumeOrderImbalanceParameter()
        factor = VolumeOrderImbalance(symbol, orderbook, param)

        got = factor.get()
        want = 9  # 11 - (14 - 12)
        self.assertEqual(want, got)

    def test_get_bid_p_no_change_ask_p_change(self):
        symbol = 'DUMMY_SYMBOL'
        orderbook = Orderbook(symbol)

        snapshot1 = OrderbookSnapshot(symbol)
        snapshot1.bid_prices.append(100)
        snapshot1.bid_sizes.append(10)
        snapshot1.ask_prices.append(110)
        snapshot1.ask_sizes.append(12)
        snapshot1.epoch_seconds = 0
        orderbook.on_update(snapshot1)

        snapshot2 = OrderbookSnapshot(symbol)
        snapshot2.bid_prices.append(100)
        snapshot2.bid_sizes.append(11)
        snapshot2.ask_prices.append(109)
        snapshot2.ask_sizes.append(14)
        snapshot2.epoch_seconds = 60
        orderbook.on_update(snapshot2)

        param = VolumeOrderImbalanceParameter()
        factor = VolumeOrderImbalance(symbol, orderbook, param)

        got = factor.get()
        want = -13  # (11 - 10) - 14
        self.assertEqual(want, got)

    def test_get_bid_p_decrease_ask_p_increase(self):
        symbol = 'DUMMY_SYMBOL'
        orderbook = Orderbook(symbol)

        snapshot1 = OrderbookSnapshot(symbol)
        snapshot1.bid_prices.append(100)
        snapshot1.bid_sizes.append(10)
        snapshot1.ask_prices.append(110)
        snapshot1.ask_sizes.append(12)
        snapshot1.epoch_seconds = 0
        orderbook.on_update(snapshot1)

        snapshot2 = OrderbookSnapshot(symbol)
        snapshot2.bid_prices.append(99)
        snapshot2.bid_sizes.append(11)
        snapshot2.ask_prices.append(111)
        snapshot2.ask_sizes.append(14)
        snapshot2.epoch_seconds = 60
        orderbook.on_update(snapshot2)

        param = VolumeOrderImbalanceParameter()
        factor = VolumeOrderImbalance(symbol, orderbook, param)

        got = factor.get()
        want = 0  # 0 - 0
        self.assertEqual(want, got)
