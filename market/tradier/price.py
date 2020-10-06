import os, json
import market.tradier.common
import requests

_URL_PATH_FORMAT_QUOTES = '/markets/quotes'


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
        pass

    def get_price(self, symbol):
        response = requests.get(market.tradier.common.URL_BASE_TRADIER + _URL_PATH_FORMAT_QUOTES,
                          params={'symbols': symbol},
                          headers=market.tradier.common.get_auth_header_tradier()
                          )
        if response.status_code != 200:
            return 0
        js = response.json()
        quote_list = js['quotes']['quote']
        quote_list = quote_list if type(quote_list) is list else [quote_list]

        for quote in quote_list:
            if quote['symbol'] == symbol:
                return quote['last']
        return 0

    def get_quote(self, symbol):
        # TODO: implement
        p = self.get_price(symbol)
        return p, p

    def get_bidask_spread(self, symbol):
        b, a = self.get_quote(symbol)
        if b == 0 and a == 0:
            return 0
        return (a - b) / b
