import util.logging
import util.current_time as current_time
import time, threading
from strategy.strategy import TICK_TIMEBUCKET_SECONDS


class TradeStrategyRun():
    def __init__(self, positionsize, long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
                 symbol_to_strategy,
                 a_current_time = None, to_start_tick_timebucket_thread = True):
        util.logging.log_to_std = False

        self.last_tick_epoch_second = 0
        self.current_time = a_current_time if a_current_time else current_time.CurrentTime()
        self.tick_minute_sleep_duration_seconds = 2
        self.positionsize = positionsize

        self.long_enter = long_enter
        self.long_exit = long_exit
        self.short_enter = short_enter
        self.short_exit = short_exit
        self.long_enter_dryrun = long_enter_dryrun
        self.long_exit_dryrun = long_exit_dryrun
        self.short_enter_dryrun = short_enter_dryrun
        self.short_exit_dryrun = short_exit_dryrun

        if to_start_tick_timebucket_thread:
            threading.Thread(target=self._tick_timebucket).start()

        self.symbol_to_strategy = symbol_to_strategy

        self.daily_trade_started = True

    def _is_tick_new_timebucket(self):
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        return epoch_seconds // TICK_TIMEBUCKET_SECONDS - self.last_tick_epoch_second // TICK_TIMEBUCKET_SECONDS > 0

    def _tick_timebucket(self):
        while True:
            if self._is_tick_new_timebucket():
                self.on_new_timebucket()
                self.last_tick_epoch_second = self.current_time.get_current_epoch_seconds()
            time.sleep(self.tick_minute_sleep_duration_seconds)

    def on_new_timebucket(self):
        pass

    def on_daily_trade_start(self):
        util.logging.info('on_daily_trade_start')
        self.clean()
        self.daily_trade_started = True

    def clean(self):
        pass

    def save_daily_df(self, base_dir='data'):
        pass

    def on_daily_trade_end(self, base_dir='data'):
        util.logging.info('on_daily_trade_end')
        self.daily_trade_started = False

