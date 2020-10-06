import market.ally.allypy as ally
import market.ally.common
from market.dry_run.short.enter import ShortDryRun
import os, threading, datetime
import util.logging

class Short:
    def __init__(self, market_price):
        self.a = market.ally.common.get_client()
        self.account = os.getenv('ALLY_ACCOUNT_NBR')
        self.market_price = market_price

    def _short(self, enter_plan):
        symbol, price, quantity = enter_plan.plan(self.market_price)
        util.logging.info('shorting {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=enter_plan.symbol, quantity=quantity, target_price = enter_plan.target_price, price=price))

        try:
            order = ally.order.Order(

                # Good for day order
                timespan=ally.order.Timespan('day'),

                # Buy order (to_open is True by defaul)
                type=ally.order.Sell(True),

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

            util.logging.info('submitted a short enter order for {symbol}, response: {response}'.format(symbol=symbol, response=exec_status))
            return exec_status
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
