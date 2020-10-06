import pprint
import market.binance.common

class HoldingsNoOp:
    def get(self):
        return {}

    def get_quantity(self, symbol):
        return 0

class Holdings:
    def __init__(self):
        self.client = market.binance.common.get_client()

    def _print_account_info(self):
        account_info = self.client.get_account()
        pprint.pprint(account_info)

    def get(self):
        account_info = self.client.get_account()
        return {b['asset'] : float(b['free']) for b in account_info['balances']}

    def get_quantity(self, symbol):
        holdings = self.get()
        coin_symbol = symbol.replace('USDT', '')
        if coin_symbol not in holdings:
            return 0
        return holdings[coin_symbol]

    def get_borrowed_quantity(self, symbol):
        return self.get_quantity(symbol)
