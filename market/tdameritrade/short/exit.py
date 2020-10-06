import market.tdameritrade.common
from market.dry_run.short.exit import ClearShortDryRun
from tda.orders import EquityOrderBuilder, Duration, Session
import os, threading, datetime
import util.logging

_ACCOUNT_NUMBER = os.getenv('TD_ACCOUNT_ID')
_INSTRUCTION_BUY_TO_COVER = 'BUY_TO_COVER'

class ClearShort:
    def __init__(self, market_price, margin_holding):
        self.market_price = market_price
        self.holding = margin_holding
        self.client = market.tdameritrade.common.get_client()

    def _exit_short(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holding)
        quantity = round(quantity - 0.0005, 3)
        util.logging.info('clearing short, buying back all positions {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))

        try:
            order_builder = EquityOrderBuilder(symbol, quantity). \
                set_instruction(EquityOrderBuilder.Instruction.BUY). \
                set_order_type(EquityOrderBuilder.OrderType.MARKET). \
                set_duration(Duration.DAY). \
                set_session(Session.NORMAL)

            order_spec = order_builder.build()
            for leg in order_spec['orderLegCollection']:
                leg['instruction'] = _INSTRUCTION_BUY_TO_COVER

            response = self.client.place_order(_ACCOUNT_NUMBER, order_spec)
            if not response or not response.ok:
                return {}

            js = response.json()
            util.logging.info('submitted a short enter order for {symbol}, response: {response}'.format(symbol=symbol, response=js))
            return js
        except Exception as ex:
            util.logging.error('an exception happened while clearing short for {symbol}, {e}'.format(symbol=symbol, e=str(ex)))
            return {}

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
