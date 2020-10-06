import market.binance.common

class MockPrice:
    def __init__(self):
        pass

    def get_price(self, symbol):
        return 50.0

    def get_quote(self, symbol):
        return 50.0, 50.1

    def get_bidask_spread(self, symbol):
        b, a = self.get_quote(symbol)
        if b == 0 and a == 0:
            return 0
        return (a - b) / b

class Price:
    def __init__(self):
        self.client = market.binance.common.get_client()

    def get_price(self, symbol):
        b, a = self.get_quote(symbol)
        if b == 0:
            return a
        elif a == 0:
            return b
        else:
            return (a+b) / 2.0

    def get_quote(self, symbol):
        depth = self.client.get_order_book(symbol=symbol)
        ask = None
        if len(depth['asks']) > 0:
            ask = float(depth['asks'][0][0])
        bid = None
        if len(depth['bids']) > 0:
            bid = float(depth['bids'][0][0])
        if ask is None and bid is None:
            return 0.0
        elif bid is None:
            return ask
        elif ask is None:
            return bid

        return bid, ask

    def get_bidask_spread(self, symbol):
        b, a = self.get_quote(symbol)
        if b == 0 and a == 0:
            return 0
        return (a - b) / b
