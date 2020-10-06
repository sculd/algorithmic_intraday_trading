from strategy.factors.orderbook_factors.factor import OrderbookFactor
import util.logging

import numpy as np
from enum import Enum

class AverageTradePriceParameter:
    def __init__(self):
        pass


class AverageTradePrice(OrderbookFactor):
    def __init__(self, symbol, orderbook, param):
        super().__init__(symbol, orderbook)
        self.param = param
        self.prev_tp = 0

    def get(self):
        p_b_t = self.orderbook.snapshot.get_bid_price()
        p_a_t = self.orderbook.snapshot.get_ask_price()
        tp = 1.0 * (p_b_t + p_a_t) / 2.0
        if self.prev_tp == 0:
            self.prev_tp = tp
            return tp

        v_t = self.orderbook.snapshot.last_size
        v_t_1 = self.orderbook.prev_snapshot.last_size

        if v_t == v_t_1:
            return self.prev_tp

        p_t = self.orderbook.snapshot.last_price
        p_t_1 = self.orderbook.prev_snapshot.last_price

        tp = 1.0 * (p_t - p_t_1) / (v_t - v_t_1)
        self.prev_tp = tp

        return tp
