import market.ally.allypy as ally
import market.ally.common
import os, datetime, threading
import market.ally.holdings
import util.logging


class SellDryRun:
    def __init__(self, market_price):
        self.market_price = market_price
        self.holdings = market.ally.holdings.Holdings()

    def _sell(self, plan):
        quantity = self.holdings.get_quantity(plan.symbol)
        price = self.market_price.get_price(plan.symbol)
        util.logging.info('(dry_run) selling all positions for {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=plan.symbol, quantity=quantity, target_price = plan.target_price, price=price))

    def _sell_thread(self, plan):
        threading.Thread(target=self._sell, args=(plan,)).start()

    def sell_all(self, plan):
        self._sell_thread(plan)

class Sell:
    def __init__(self, market_price):
        self.a = market.ally.common.get_client()
        self.account = int(os.getenv('ALLY_ACCOUNT_NBR'))
        self.holdings = market.ally.holdings.Holdings()
        self.market_price = market_price

    def _sell(self, plan):
        quantity = self.holdings.get_quantity(plan.symbol)
        price = self.market_price.get_price(plan.symbol)
        util.logging.info('elling all positions for {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=plan.symbol, quantity=quantity, target_price = plan.target_price, price=price))

        order = ally.order.Order(

            # Good for day order
            timespan=ally.order.Timespan('day'),

            # Buy order (to_open is True by defaul)
            type=ally.order.Sell(),

            # Market order
            price=ally.order.Market(),

            # Stock, symbol F
            instrument=ally.instrument.Equity(plan.symbol),

            quantity=ally.order.Quantity(quantity)
        )

        exec_status = self.a.submit_order(

            # specify order created, see above
            order=order,

            # Can dry-run using preview=True, defaults to True
            # Must specify preview=False to actually execute
            preview=False,

            # Like always, if not specified in environment, use a specific account
            account=self.account
        )

        return exec_status

    def _sell_thread(self, plan):
        threading.Thread(target=self._sell, args=(plan,)).start()

    def sell_all(self, plan):
        self._sell_thread(plan)


_sell = None
def get_sell(market_price, dry_run):
    global _sell
    if _sell is not None:
        return _sell

    if dry_run:
        res = SellDryRun(market_price)
    else:
        res = Sell(market_price)
    _sell = res
    return res
