import market.binance.common
import os, threading
import util.logging
from binance.enums import *

class ExitLongDryRun:
    def __init__(self, market_price, holding):
        self.market_price = market_price
        self.holding = holding

    def _exit_long(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holding)
        util.logging.info('(dry_run) clearing long {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))

    def _exit_long_thread(self, exit_plan):
        threading.Thread(target=self._exit_long, args=(exit_plan,)).start()

    def exit(self, exit_plan):
        util.logging.debug('(dry_run) longDryRun.exit')
        self._exit_long_thread(exit_plan)

class ExitLong:
    def __init__(self, market_price, holding):
        self.client = market.binance.common.get_client()
        self.market_price = market_price
        self.holding = holding
        self.lot_sizes = market.binance.common.get_lot_sizes()

    def _exit_long(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holding)
        lot_size = self.lot_sizes[symbol] if symbol in self.lot_sizes else 0.001
        lot_size *= 10
        quantity = int(quantity / lot_size) * lot_size
        util.logging.info('clearing long {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))

        try:
            order = self.client.create_margin_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=quantity)
            util.logging.debug('For {symbol} exit long (sell) order from binance: {order}'.format(
                symbol=symbol, order=str(order)))
            return order
        except Exception as ex:
            util.logging.error(str(ex))
            return None

    def _exit_long_thread(self, exit_plan):
        threading.Thread(target=self._exit_long, args=(exit_plan,)).start()

    def exit(self, exit_plan):
        '''

        :param plan: map of symbol to quantity
        :return:
        '''
        self._exit_long_thread(exit_plan)


_buy = None
def get_exit_long(market_price, holding, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = ExitLongDryRun(market_price, holding)
    else:
        res = ExitLong(market_price, holding)
    _buy = res
    return res
