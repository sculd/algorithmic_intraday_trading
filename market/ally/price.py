import os, json
import market.ally.common
import requests

_API_KEY = os.environ['API_KEY_POLYGON']

class Price:
    def __init__(self):
        self.a = market.ally.common.get_client()
        self.account = os.getenv('ALLY_ACCOUNT_NBR')

    def get_price(self, symbol):
        b, a = self.get_quote(symbol)
        if b == 0:
            return a
        elif a == 0:
            return b
        else:
            return (a+b) / 2.0

    def get_quote(self, symbol):
        q = self.a.get_quote(
            symbols="{symbol}".format(symbol=symbol),
            fields="bid,ask"
        )
        a = float(q['ask'])
        b = float(q['bid'])
        if a == 0:
            try:
                url = 'https://api.polygon.io/v1/last_quote/stocks/{symbol}?apiKey={apiKey}'.format(symbol=symbol, apiKey=_API_KEY)
                res = requests.get(url)
                js = res.json()
                b = js['last']['bidprice']
            except Exception as e:
                print(e)
        a = float(q['ask'])
        if a == 0:
            try:
                url = 'https://api.polygon.io/v1/last_quote/stocks/{symbol}?apiKey={apiKey}'.format(symbol=symbol, apiKey=_API_KEY)
                res = requests.get(url)
                js = res.json()
                a = js['last']['askprice']
            except Exception as e:
                print(e)
        return b, a

    def get_bidask_spread(self, symbol):
        b, a = self.get_quote(symbol)
        if b == 0 and a == 0:
            return 0
        return (a - b) / b
