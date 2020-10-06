import market.ally.allypy as ally
import market.ally.common
from market.dry_run.long.exit import ExitLongDryRun
import os, datetime, threading
import util.logging


class ExitLong:
    def __init__(self, market_price, holding):
        self.a = market.ally.common.get_client()
        self.account = os.getenv('ALLY_ACCOUNT_NBR')
        self.market_price = market_price
        self.holding = holding

    def _exit_long(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holding)
        quantity = round(quantity, 3)
        util.logging.info('selling all positions for {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))
        if quantity == 0:
            util.logging.warning('trying to sell positions for {symbol} but the quantity is zero, thus doing nothing, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, target_price=exit_plan.target_price, price=price))
            return None

        try:
            order = ally.order.Order(

                # Good for day order
                timespan=ally.order.Timespan('day'),

                # Buy order (to_open is True by defaul)
                type=ally.order.Sell(False),

                # Market order
                price=ally.order.Market(),

                # Stock, symbol F
                instrument=ally.instrument.Equity(symbol),

                quantity=ally.order.Quantity(quantity)
            )

            util.logging.info('submitting a long exit order for {symbol}, order: {order}'.format(symbol=symbol, order=order))
            exec_status = self.a.submit_order(

                # specify order created, see above
                order=order,

                # Can dry-run using preview=True, defaults to True
                # Must specify preview=False to actually execute
                preview=False,

                # Like always, if not specified in environment, use a specific account
                account=self.account
            )

            util.logging.info('submitted a long exit order for {symbol}, response: {response}'.format(symbol=symbol, response=exec_status))
            return exec_status
        except Exception as ex:
            util.logging.error('an exception happened while clearing long for {symbol}, {e}'.format(symbol=symbol, e=str(ex)))
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
