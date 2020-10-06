import market.tdameritrade.common
from market.dry_run.long.exit import ExitLongDryRun
from tda.orders import EquityOrderBuilder, Duration, Session
import os, datetime, threading
import util.logging

_ACCOUNT_NUMBER = os.getenv('TD_ACCOUNT_ID')


class ExitLong:
    def __init__(self, market_price, holding):
        self.market_price = market_price
        self.holding = holding
        self.client = market.tdameritrade.common.get_client()

    def _exit_long(self, exit_plan):
        symbol, price, quantity = exit_plan.plan(self.market_price, self.holding)
        quantity = round(quantity, 3)
        util.logging.info('selling all positions for {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))
        if quantity == 0:
            util.logging.warning('trying to sell positions for {symbol} but the quantity is zero, thus doing nothing, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, target_price=exit_plan.target_price, price=price))
            return None

        try:
            order_builder = EquityOrderBuilder(symbol, quantity). \
                set_instruction(EquityOrderBuilder.Instruction.SELL). \
                set_order_type(EquityOrderBuilder.OrderType.MARKET). \
                set_duration(Duration.DAY). \
                set_session(Session.NORMAL)

            order_spec = order_builder.build()


            response = self.client.place_order(_ACCOUNT_NUMBER, order_spec)
            if not response or not response.ok:
                return {}

            js = response.json()
            util.logging.info('submitted a long exit order for {symbol}, response: {response}'.format(symbol=symbol, response=js))
            return js
        except Exception as ex:
            util.logging.error('an exception happened while clearing long for {symbol}, {e}'.format(symbol=symbol, e=str(ex)))
            return {}

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
