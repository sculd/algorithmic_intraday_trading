import market.tradier.common
from market.dry_run.short.exit import ClearShortDryRun
import os, datetime, time, requests, threading
import util.logging

_URL_PATH_FORMAT_ORDER = '/accounts/{account_id}/orders'

class ClearShort:
    def __init__(self, market_price, margin_holding):
        self.account_number = market.tradier.common.get_account_account_number()
        self.market_price = market_price
        self.holding = margin_holding

    def _exit_short(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holding)
        quantity = round(quantity - 0.0005, 3)
        util.logging.info('clearing short {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))

        try:
            response = requests.post(market.tradier.common.URL_BASE_TRADIER + _URL_PATH_FORMAT_ORDER.format(account_id=self.account_number),
                                     data={'class': 'equity', 'symbol': symbol, 'side': 'buy_to_cover', 'quantity': str(quantity),
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

    def _exit_short_thread(self, short_exit_plan):
        threading.Thread(target=self._exit_short, args=(short_exit_plan,)).start()

    def exit(self, short_exit_plan):
        '''

        :param short_exit_plan: map of symbol to quantity
        :return:
        '''
        self._exit_short_thread(short_exit_plan)

_buy = None
def get_exit_short(market_price, holding, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = ClearShortDryRun(market_price, holding)
    else:
        res = ClearShort(market_price, holding)
    _buy = res
    return res
