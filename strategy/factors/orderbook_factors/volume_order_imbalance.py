from strategy.factors.orderbook_factors.factor import OrderbookFactor
import util.logging

from enum import Enum

class VolumeOrderImbalanceParameter:
    def __init__(self):
        pass


class VolumeOrderImbalance(OrderbookFactor):
    def __init__(self, symbol, orderbook, param):
        super().__init__(symbol, orderbook)
        self.param = param

    def get(self):
        p_b_t = self.orderbook.snapshot.get_bid_price()
        p_b_t_1 = self.orderbook.prev_snapshot.get_bid_price()
        v_b_t = self.orderbook.snapshot.get_bid_volume()
        v_b_t_1 = self.orderbook.prev_snapshot.get_bid_volume()
        delta_volume_bid = 0
        if p_b_t > p_b_t_1:
            delta_volume_bid += v_b_t
        elif p_b_t == p_b_t_1:
            delta_volume_bid += v_b_t - v_b_t_1

        p_a_t = self.orderbook.snapshot.get_ask_price()
        p_a_t_1 = self.orderbook.prev_snapshot.get_ask_price()
        v_a_t = self.orderbook.snapshot.get_ask_volume()
        v_a_t_1 = self.orderbook.prev_snapshot.get_ask_volume()
        delta_volume_ask = 0
        if p_a_t < p_a_t_1:
            delta_volume_ask += v_a_t
        elif p_a_t == p_a_t_1:
            delta_volume_ask += v_a_t - v_a_t_1

        return delta_volume_bid - delta_volume_ask
