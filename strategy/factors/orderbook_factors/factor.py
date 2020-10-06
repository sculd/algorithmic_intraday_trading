from ingest.streaming.orderbook import Orderbook
from strategy.factors.factor import Factor


class OrderbookFactor(Factor):
    def __init__(self, symbol, orderbook):
        super().__init__(symbol)
        self.orderbook = orderbook

    def get(self):
        pass
