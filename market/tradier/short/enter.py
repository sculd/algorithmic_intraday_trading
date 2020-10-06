import market.tradier.common
from market.dry_run.short.enter import ShortDryRun
import market.tradier.etb
import os, datetime, time, requests, threading
import util.logging

_URL_PATH_FORMAT_ORDER = '/accounts/{account_id}/orders'

class Short:
    def __init__(self, market_price):
        self.account_number = market.tradier.common.get_account_account_number()
        self.market_price = market_price

    def _short(self, enter_plan):
        symbol, price, quantity = enter_plan.plan(self.market_price)
        util.logging.info('shorting {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=enter_plan.symbol, quantity=quantity, target_price = enter_plan.target_price, price=price))

        try:
            etb = market.tradier.etb.get_etb()
            if symbol not in etb:
                util.logging.warning('symbol {symbol} is not available for short in tradier'.format(symbol = symbol))

            response = requests.post(market.tradier.common.URL_BASE_TRADIER + _URL_PATH_FORMAT_ORDER.format(account_id=self.account_number),
                                     data={'class': 'equity', 'symbol': symbol, 'side': 'sell_short', 'quantity': str(quantity),
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

    def _short_thread(self, enter_plan):
        threading.Thread(target=self._short, args=(enter_plan,)).start()

    def enter(self, enter_plan):
        '''

        :param enter_plan: map of symbol to quantity
        :return:
        '''
        self._short_thread(enter_plan)


_buy = None
def get_short(market_price, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = ShortDryRun(market_price)
    else:
        res = Short(market_price)
    _buy = res
    return res
