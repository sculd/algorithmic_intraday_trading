import os, json
import market.tdameritrade.common


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
        self.client = market.tdameritrade.common.get_client()

    def get_price(self, symbol):
        b, a = self.get_quote(symbol)
        if b == 0:
            return a
        elif a == 0:
            return b
        else:
            return (a+b) / 2.0

    def get_quote(self, symbol):
        resp = self.client.get_quote(symbol)

        if not resp.ok:
            return 0, 0

        js = resp.json()
        return js[symbol]['bidPrice'], js[symbol]['askPrice']

    def get_bidask_spread(self, symbol):
        b, a = self.get_quote(symbol)
        if b == 0 and a == 0:
            return 0
        return (a - b) / b
