import os, datetime, threading
import util.logging


class ExitLongDryRun:
    def __init__(self, market_price, holding):
        self.market_price = market_price
        self.holdings = holding

        # to avoid violating the throttle
        self.datetime_last_request = datetime.datetime.utcnow()
        self.prev_price = 0

    def _exit_long(self, exit_plan):
        now = datetime.datetime.utcnow()
        dt = now - self.datetime_last_request
        price, quantity = self.prev_price, 1
        if dt.seconds >= 1:
            quantity = self.holdings.get_quantity(exit_plan.symbol)
            price = self.market_price.get_price(exit_plan.symbol)
        util.logging.info('(dry_run) selling all positions for {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(symbol=exit_plan.symbol, quantity=quantity, target_price = exit_plan.target_price, price=price))
        self.datetime_last_request = datetime.datetime.utcnow()

    def _exit_long_thread(self, exit_plan):
        threading.Thread(target=self._exit_long, args=(exit_plan,)).start()

    def exit(self, exit_plan):
        self._exit_long_thread(exit_plan)
