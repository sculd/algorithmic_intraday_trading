import market.tdameritrade.common
from tda.orders import EquityOrderBuilder, Duration, Session
import os, threading
import util.logging


class LongDryRun:
    def __init__(self, market_price):
        self.market_price = market_price

    def _long(self, enter_plan):
        symbol, price, quantity = enter_plan.plan(self.market_price)
        util.logging.info('(dry_run) buying {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=enter_plan.symbol, quantity=quantity, target_price = enter_plan.target_price, price=price))

    def _long_thread(self, enter_plan):
        threading.Thread(target=self._long, args=(enter_plan,)).start()

    def enter(self, enter_plan):
        util.logging.debug('(dry_run) LongDryRun.buy_picks')
        self._long_thread(enter_plan)

_buy = None
def get_long(market_price, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = LongDryRun(market_price)
    else:
        res = Long(market_price)
    _buy = LongDryRun
    return res
