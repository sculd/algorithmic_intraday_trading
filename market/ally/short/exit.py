import market.ally.allypy as ally
import market.ally.common
from market.dry_run.short.exit import ClearShortDryRun
import os, threading, datetime
import util.logging

class ClearShort:
    def __init__(self, market_price, margin_holding):
        self.a = market.ally.common.get_client()
        self.account = os.getenv('ALLY_ACCOUNT_NBR')
        self.market_price = market_price
        self.holding = margin_holding

    def _exit_short(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holding)
        quantity = round(quantity - 0.0005, 3)
        util.logging.info('clearing short, buying back all positions {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))

        try:
            order = ally.order.Order(

                # Good for day order
                timespan=ally.order.Timespan('day'),

                # Buy order (to_open is True by defaul)
                type=ally.order.Buy(False),

                # Market order
                price=ally.order.Market(),

                # Stock, symbol F
                instrument=ally.instrument.Equity(symbol),

                quantity=ally.order.Quantity(quantity)
            )

            util.logging.info('submitting a short exit order for {symbol}, order: {order}'.format(symbol=symbol, order=order))
            exec_status = self.a.submit_order(

                # specify order created, see above
                order=order,

                # Can dry-run using preview=True, defaults to True
                # Must specify preview=False to actually execute
                preview=False,

                # Like always, if not specified in environment, use a specific account
                account=self.account
            )

            util.logging.info('submitted a short exit order for {symbol}, response: {response}'.format(symbol=symbol, response=exec_status))
            return exec_status
        except Exception as ex:
            util.logging.error('an exception happened while clearing short for {symbol}, {e}'.format(symbol=symbol, e=str(ex)))
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
