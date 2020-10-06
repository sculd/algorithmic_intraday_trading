import os, datetime, threading
import util.logging

class LongDryRun:
    def __init__(self, market_price):
        self.market_price = market_price

        # to avoid violating the throttle
        self.datetime_last_request = datetime.datetime.utcnow()
        self.prev_price = 0

    def _long(self, enter_plan):
        now = datetime.datetime.utcnow()
        dt = now - self.datetime_last_request
        symbol, price, quantity = enter_plan.symbol, self.prev_price, 1
        if dt.seconds >= 1:
            symbol, price, quantity = enter_plan.plan(self.market_price)
        util.logging.info('(dry_run) buying {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=enter_plan.symbol, quantity=quantity, target_price = enter_plan.target_price, price=price))
        self.datetime_last_request = datetime.datetime.utcnow()

    def _long_thread(self, enter_plan):
        threading.Thread(target=self._long, args=(enter_plan,)).start()

    def enter(self, enter_plan):
        util.logging.debug('(dry_run) LongDryRun.buy_picks')
        self._long_thread(enter_plan)
