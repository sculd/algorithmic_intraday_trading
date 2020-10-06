from strategy.run import TradeStrategyRun


class OrderbookStrategyRun(TradeStrategyRun):
    def __init__(self, positionsize, long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
                 symbol_to_strategy,
                 a_current_time = None, to_start_tick_timebucket_thread = True):
        self.strategy_per_symbol = {}
        super().__init__(positionsize, long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
                 symbol_to_strategy,
                 a_current_time = a_current_time, to_start_tick_timebucket_thread = to_start_tick_timebucket_thread)

    def on_orderbook_snapshot(self, orderbook_snapshot):
        if not self.daily_trade_started: return
        symbol = orderbook_snapshot.symbol
        if symbol not in self.strategy_per_symbol:
            self.strategy_per_symbol[symbol] = self.symbol_to_strategy(symbol)
        self.strategy_per_symbol[symbol].on_orderbook_snapshot(orderbook_snapshot)

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
        super().on_daily_trade_end(base_dir=base_dir)
        for _, strategy in self.strategy_per_symbol.items():
            strategy.on_daily_trade_end()

