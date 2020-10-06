from strategy.run import TradeStrategyRun
import util.logging


class BarWithTimeTradeStrategyRun(TradeStrategyRun):
    def __init__(self, positionsize, long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
                 symbol_to_strategy,
                 a_current_time = None, to_start_tick_timebucket_thread = True):
        self.strategy_per_symbol = {}
        super().__init__(positionsize, long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
                 symbol_to_strategy,
                 a_current_time = a_current_time, to_start_tick_timebucket_thread = to_start_tick_timebucket_thread)
        self.strategy_per_symbol = {}

    def on_bar_with_time(self, bar_with_time):
        if not self.daily_trade_started: return
        if bar_with_time.bar.symbol not in self.strategy_per_symbol:
            self.strategy_per_symbol[bar_with_time.bar.symbol] = self.symbol_to_strategy(bar_with_time.bar.symbol)
        self.strategy_per_symbol[bar_with_time.bar.symbol].on_bar_with_time(bar_with_time)

    def on_trade(self, trade):
        if not self.daily_trade_started: return
        if trade.symbol not in self.strategy_per_symbol:
            self.strategy_per_symbol[trade.symbol] = self.symbol_to_strategy(trade.symbol)
        self.strategy_per_symbol[trade.symbol].on_trade(trade)

    def on_new_timebucket(self):
        for _, strategy in self.strategy_per_symbol.items():
            strategy.on_new_timebucket()
        super().on_new_timebucket()

    def on_daily_trade_start(self):
        super().on_daily_trade_start()

    def clean(self):
        self.strategy_per_symbol = {}
        super().clean()

    def save_daily_df(self, base_dir='data'):
        super().save_daily_df(base_dir=base_dir)

    def on_daily_trade_end(self, base_dir='data'):
        util.logging.info('strategy run.on_daily_trade_end')
        super().on_daily_trade_end(base_dir=base_dir)
        for _, strategy in self.strategy_per_symbol.items():
            strategy.on_daily_trade_end()

