import market.tdameritrade.common
import os, threading
import util.logging



class Short:
    def __init__(self, market_price, quote_short_enter, base_long_enter):
        '''
        quote is short, base is long
        '''
        self.market_price = market_price
        self.client = market.tdameritrade.common.get_client()
        self.quote_short_enter = quote_short_enter
        self.base_long_enter = base_long_enter

    def _short(self, enter_plan):
        self.quote_short_enter.enter(enter_plan.child_plan)
        self.base_long_enter.enter(enter_plan.parent_plan)

    def _short_thread(self, enter_plan):
        threading.Thread(target=self._short, args=(enter_plan,)).start()

    def enter(self, enter_plan):
        '''

        :param enter_plan: map of symbol to quantity
        :return:
        '''
        self._short_thread(enter_plan)

_buy = None
def get_short(market_price, quote_short_enter, base_long_enter):
    global _buy
    if _buy is not None:
        return _buy

    res = Short(market_price, quote_short_enter, base_long_enter)
    _buy = res
    return res
