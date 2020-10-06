import market.tradier.common
from market.dry_run.long.exit import ExitLongDryRun
import os, requests, datetime, threading
import util.logging

_URL_PATH_FORMAT_ORDER = '/accounts/{account_id}/orders'


class ExitLong:
    def __init__(self, market_price, holding):
        self.account_number = market.tradier.common.get_account_account_number()
        self.market_price = market_price
        self.holding = holding

    def _exit_long(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holding)
        quantity = round(quantity, 3)
        util.logging.info('selling all positions for {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))
        if quantity == 0:
            util.logging.warning('trying to sell positions for {symbol} but the quantity is zero, thus doing nothing, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, target_price=exit_plan.target_price, price=price))
            return None

        try:
            response = requests.post(market.tradier.common.URL_BASE_TRADIER + _URL_PATH_FORMAT_ORDER.format(account_id=self.account_number),
                                     data={'class': 'equity', 'symbol': symbol, 'side': 'sell', 'quantity': str(quantity),
                                           'type': 'market', 'duration': 'day'},
                                     headers=market.tradier.common.get_auth_header_tradier()
                                     )
            if response.status_code != 200:
                return {}
            js = response.json()
            print(js)
            return js
        except Exception as ex:
            util.logging.error(str(ex))
            return None

    def _exit_long_thread(self, exit_plan):
        threading.Thread(target=self._exit_long, args=(exit_plan,)).start()

    def exit(self, exit_plan):
        self._exit_long_thread(exit_plan)


_sell = None
def get_exit_long(market_price, holding, dry_run):
    global _sell
    if _sell is not None:
        return _sell

    if dry_run:
        res = ExitLongDryRun(market_price, holding)
    else:
        res = ExitLong(market_price, holding)
    _sell = res
    return res
