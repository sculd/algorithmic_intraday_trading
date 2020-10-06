import market.binance.common
import pprint

class MarginHoldings:
    def __init__(self):
        self.client = market.binance.common.get_client()

    def _print_account_info(self):
        account_info = self.client.get_account()
        pprint.pprint(account_info)

    def get_free(self):
        account_info = self.client.get_margin_account()
        return {b['asset'] : float(b['free']) for b in account_info['userAssets']}

    def get_borrowed(self):
        account_info = self.client.get_margin_account()
        return {b['asset'] : float(b['borrowed']) for b in account_info['userAssets']}

    def get_quantity(self, symbol):
        holdings = self.get_free()
        coin_symbol = symbol.replace('USDT', '')
        if coin_symbol not in holdings:
            return 0
        return holdings[coin_symbol]

    def get_borrowed_quantity(self, symbol):
        holdings = self.get_borrowed()
        coin_symbol = symbol.replace('USDT', '')
        if coin_symbol not in holdings:
            return 0
        return holdings[coin_symbol]

