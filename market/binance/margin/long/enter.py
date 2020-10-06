import market.binance.common
import os, threading
import util.logging
from binance.enums import *

class LongDryRun:
    def __init__(self, market_price):
        self.market_price = market_price

    def _long(self, buy_plan):
        symbol, price, quantity = buy_plan.plan(self.market_price)
        util.logging.info('(dry_run) longing {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=buy_plan.symbol, quantity=quantity, target_price = buy_plan.target_price, price=price))

    def _long_thread(self, enter_plan):
        threading.Thread(target=self._long, args=(enter_plan,)).start()

    def enter(self, enter_plan):
        util.logging.debug('(dry_run) longDryRun.enter')
        self._long_thread(enter_plan)

class Long:
    def __init__(self, market_price):
        self.client = market.binance.common.get_client()
        self.market_price = market_price

    def _long(self, enter_plan):
        symbol, price, quantity = enter_plan.plan(self.market_price)
        util.logging.info('buying {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = enter_plan.target_price, price=price))

        try:
            order = self.client.create_margin_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=quantity)
            import pprint
            pprint.pprint(order)

            util.logging.debug('For {symbol} long (buy) order from binance: {order}'.format(
                symbol=symbol, order=str(order)))
            return order
        except Exception as ex:
            util.logging.error(str(ex))
            return None

    def _long_thread(self, enter_plan):
        threading.Thread(target=self._long, args=(enter_plan,)).start()

    def enter(self, enter_plan):
        '''

        :param enter_plan: map of symbol to quantity
        :return:
        '''
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
    _buy = res
    return res
