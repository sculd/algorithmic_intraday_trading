import market.ally.allypy as ally
import market.ally.common
import os, datetime, time, requests, threading
import market.ally.price
import util.logging

class BuyDryRun:
    def __init__(self, market_price):
        self.market_price = market_price

    def _buy(self, buy_plan):
        symbol, price, quantity = buy_plan.plan(self.market_price)
        util.logging.info('(dry_run) buying {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=buy_plan.symbol, quantity=quantity, target_price = buy_plan.target_price, price=price))

    def _buy_thread(self, buy_plan):
        threading.Thread(target=self._buy, args=(buy_plan,)).start()

    def buy_picks(self, buy_plan):
        self._buy_thread(buy_plan)

class Buy:
    def __init__(self, market_price):
        self.a = market.ally.common.get_client()
        self.account = os.getenv('ALLY_ACCOUNT_NBR')
        self.market_price = market_price

    def _buy(self, buy_plan):
        symbol, price, quantity = buy_plan.plan(self.market_price)
        util.logging.info('buying {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=buy_plan.symbol, quantity=quantity, target_price = buy_plan.target_price, price=price))

        order = ally.order.Order(

            # Good for day order
            timespan=ally.order.Timespan('day'),

            # Buy order (to_open is True by defaul)
            type=ally.order.Buy(),

            # Market order
            price=ally.order.Market(),

            # Stock, symbol F
            instrument=ally.instrument.Equity(symbol),

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

    def _buy_thread(self, buy_plan):
        threading.Thread(target=self._buy, args=(buy_plan,)).start()

    def buy_picks(self, buy_plan):
        '''

        :param buy_plan: map of symbol to quantity
        :return:
        '''
        self._buy_thread(buy_plan)


_buy = None
def get_buy(market_price, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = BuyDryRun(market_price)
    else:
        res = Buy(market_price)
    _buy = res
    return res
