from strategy.factors.orderbook_factors.factor import OrderbookFactor
import util.logging


class OrderImbalanceRatioParameter:
    def __init__(self):
        pass

class OrderImbalanceRatio(OrderbookFactor):
    def __init__(self, symbol, orderbook, param):
        super().__init__(symbol, orderbook)
        self.param = param

    def get(self):
        v_b_t = self.orderbook.snapshot.get_bid_volume()
        v_a_t = self.orderbook.snapshot.get_ask_volume()

        if v_b_t + v_a_t == 0:
            return 0.0
        
        return 1.0 * (v_b_t - v_a_t) / (v_b_t + v_a_t)

