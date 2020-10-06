import market.tdameritrade.common
from tda.orders import EquityOrderBuilder, Duration, Session
import os, datetime, threading
import util.logging

class ExitLong:
    def __init__(self, market_price, holding, quote_long_exit, base_short_exit):
        self.market_price = market_price
        self.holding = holding
        self.client = market.tdameritrade.common.get_client()
        self.quote_long_exit = quote_long_exit
        self.base_short_exit = base_short_exit

    def _exit_long(self, exit_plan):
        self.quote_long_exit.exit(exit_plan.child_plan)
        self.base_short_exit.exit(exit_plan.parent_plan)

    def _exit_long_thread(self, exit_plan):
        threading.Thread(target=self._exit_long, args=(exit_plan,)).start()

    def exit(self, exit_plan):
        self._exit_long_thread(exit_plan)


_sell = None
def get_exit_long(market_price, holding, quote_long_exit, base_short_exit):
    global _sell
    if _sell is not None:
        return _sell

    res = ExitLong(market_price, holding, quote_long_exit, base_short_exit)
    _sell = res
    return res
