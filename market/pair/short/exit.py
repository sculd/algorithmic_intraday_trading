import market.tdameritrade.common
from tda.orders import EquityOrderBuilder, Duration, Session
import os, datetime, threading
import util.logging


class ExitShort:
    def __init__(self, market_price, holding, quote_short_exit, base_long_exit):
        self.market_price = market_price
        self.holding = holding
        self.client = market.tdameritrade.common.get_client()
        self.quote_short_exit = quote_short_exit
        self.base_long_exit = base_long_exit

    def _exit_short(self, exit_plan):
        self.quote_short_exit.exit(exit_plan.child_plan)
        self.base_long_exit.exit(exit_plan.parent_plan)

    def _exit_short_thread(self, exit_plan):
        threading.Thread(target=self._exit_short, args=(exit_plan,)).start()

    def exit(self, exit_plan):
        self._exit_short_thread(exit_plan)


_sell = None
def get_exit_short(market_price, holding, quote_short_exit, base_long_exit):
    global _sell
    if _sell is not None:
        return _sell

    res = ExitShort(market_price, holding, quote_short_exit, base_long_exit)
    _sell = res
    return res
