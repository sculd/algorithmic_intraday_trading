import os


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
