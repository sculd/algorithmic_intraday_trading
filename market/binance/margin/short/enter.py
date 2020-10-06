import market.binance.common
import os, threading
import util.logging
from binance.enums import *

class ShortDryRun:
    def __init__(self, market_price):
        self.market_price = market_price

    def _short(self, enter_plan):
        symbol, price, quantity = enter_plan.plan(self.market_price)
        util.logging.info('(dry_run) shorting {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = enter_plan.target_price, price=price))

    def _short_thread(self, enter_plan):
        threading.Thread(target=self._short, args=(enter_plan,)).start()

    def enter(self, enter_plan):
        util.logging.debug('(dry_run) ShortDryRun.enter')
        self._short_thread(enter_plan)

class Short:
    def __init__(self, market_price):
        self.client = market.binance.common.get_client()
        self.market_price = market_price

    def _short(self, enter_plan):
        symbol, price, quantity = enter_plan.plan(self.market_price)
        coin_symbol = enter_plan.get_coin_symbol()
        util.logging.info('shorting {symbol}, coin_symbol: {coin_symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=enter_plan.symbol, coin_symbol=coin_symbol, quantity=quantity, target_price = enter_plan.target_price, price=price))

        try:
            order = self.client.create_margin_loan(asset=coin_symbol, amount=quantity * 1.002)
            util.logging.debug('For {symbol} margin loan order from binance: {order}'.format(
                symbol=symbol, order=str(order)))

            order = self.client.create_margin_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=quantity)
            util.logging.debug('For {symbol} short (sell) order from binance: {order}'.format(
                symbol=symbol, order=str(order)))
            return order
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
