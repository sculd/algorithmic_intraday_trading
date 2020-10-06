import os, threading, datetime
import util.logging

class ClearShortDryRun:
    def __init__(self, market_price, margin_holding):
        self.market_price = market_price
        self.margin_holding = margin_holding

        # to avoid violating the throttle
        self.datetime_last_request = datetime.datetime.utcnow()
        self.prev_price = 0

    def _exit_short(self, short_exit_plan):
        now = datetime.datetime.utcnow()
        dt = now - self.datetime_last_request
        symbol, price, quantity = short_exit_plan.symbol, self.prev_price, 1
        if dt.seconds >= 1:
            symbol, price, quantity = short_exit_plan.plan(self.market_price, self.margin_holding)

        util.logging.info('(dry_run) clearing short, buying back all positions {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = short_exit_plan.target_price, price=price))
        self.datetime_last_request = datetime.datetime.utcnow()

    def _exit_short_thread(self, short_exit_plan):
        threading.Thread(target=self._exit_short, args=(short_exit_plan,)).start()

    def exit(self, short_exit_plan):
        util.logging.debug('(dry_run) shortDryRun.exit')
        self._exit_short_thread(short_exit_plan)
