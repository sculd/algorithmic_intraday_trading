import market.ally.common
import os
import util.logging

class Holdings:
    def __init__(self):
        self.a = market.ally.common.get_client()
        self.account = int(os.getenv('ALLY_ACCOUNT_NBR'))
        # to avoid the bug
        try:
            self.a.get_holdings(account=self.account)
        except Exception as e:
            pass

    def get(self):
        return self.a.get_holdings(account=self.account)

    def get_quantity(self, symbol):
        holdings = self.get()
        holding_list = holdings['holding']
        holding_list = holding_list if type(holding_list) is list else [holding_list]
        print(holding_list)

        res = 0
        symbol_found = False
        for holding in holding_list:
            symbol_holding = holding['instrument']['sym']
            if symbol != symbol_holding:
                continue
            symbol_found = True
            res = abs(float(holding['qty']))

        if not symbol_found:
            util.logging.info('symbol {symbol} is not found in holdings: {holding_list}'.format(symbol=symbol, holding_list=str(holding_list)))

        return res

    def get_borrowed_quantity(self, symbol):
        return self.get_quantity(symbol)
