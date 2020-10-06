import market.binance.common
import os, datetime, threading
import util.logging


class ExitLongDryRun:
    def __init__(self, market_price, holding):
        self.market_price = market_price
        self.holdings = holding

    def _exit_long(self, exit_plan):
        quantity = self.holdings.get_quantity(exit_plan.symbol)
        price = self.market_price.get_price(exit_plan.symbol)
        util.logging.info('(dry_run) selling all positions for {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))

    def _exit_long_thread(self, exit_plan):
        threading.Thread(target=self._exit_long, args=(exit_plan,)).start()

    def exit(self, exit_plan):
        self._exit_long_thread(exit_plan)

class ExitLong:
    def __init__(self, market_price, holding):
        self.client = market.binance.common.get_client()
        self.market_price = market_price
        self.holdings = holding
        self.lot_sizes = market.binance.common.get_lot_sizes()

    def _exit_long(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holdings)
        lot_size = self.lot_sizes[symbol] if symbol in self.lot_sizes else 0.001
        lot_size *= 5
        quantity = int(quantity / lot_size) * lot_size
        price = self.market_price.get_price(exit_plan.symbol)
        util.logging.info('selling all positions for {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))

        try:
            order = self.client.order_market_sell(symbol=exit_plan.symbol, quantity=quantity)
            util.logging.debug('sell order from binance: {order}'.format(order=str(order)))
            return order
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