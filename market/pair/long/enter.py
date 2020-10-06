import market.tdameritrade.common
import os, threading
import util.logging


class Long:
    def __init__(self, market_price, quote_long_enter, base_short_enter):
        '''
        quote is long, base is short
        '''
        self.market_price = market_price
        self.client = market.tdameritrade.common.get_client()
        self.quote_long_enter = quote_long_enter
        self.base_short_enter = base_short_enter

    def _long(self, enter_plan):
        self.quote_long_enter.enter(enter_plan.child_plan)
        self.base_short_enter.enter(enter_plan.parent_plan)

    def _long_thread(self, enter_plan):
        threading.Thread(target=self._long, args=(enter_plan,)).start()

    def enter(self, enter_plan):
        '''

        :param enter_plan: map of symbol to quantity
        :return:
        '''
        self._long_thread(enter_plan)

_buy = None
def get_long(market_price, quote_long_enter, base_short_enter):
    global _buy
    if _buy is not None:
        return _buy

    res = Long(market_price, quote_long_enter, base_short_enter)
    _buy = res
    return res
