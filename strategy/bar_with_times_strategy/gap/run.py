import util.logging
import util.current_time as current_time
import market.ally.long.enter, market.ally.long.exit
import market.ally.short.enter, market.ally.short.exit
import market.ally.holdings
import market.ally.price
import market.tradier.long.enter, market.tradier.long.exit
import market.tradier.short.enter, market.tradier.short.exit
import market.tradier.holdings
import market.tradier.price
from strategy.bar_with_times_strategy.run import BarWithTimeTradeStrategyRun
import strategy.ingestion_run.bar_with_times_ingestion_run.polygon_ingestion_run
from strategy.ingestion_run.bar_with_times_ingestion_run.polygon_ingestion_run import PolygonIngestionRun
from strategy.bar_with_times_strategy.gap.strategy import GapTradeStrategy


class GapTradeStrategyRun(BarWithTimeTradeStrategyRun):
    def __init__(self, dry_run, positionsize, prev_day_closes,
                 a_current_time = None, subscription_id = None):
        self.strategy_per_symbol = {}
        util.logging.log_to_std = False

        self.last_tick_epoch_second = 0
        self.current_time = a_current_time if a_current_time else current_time.CurrentTime()
        self.tick_minute_sleep_duration_seconds = 10
        self.positionsize = positionsize

        util.logging.info('inintializing for ally broker')
        market_price = market.ally.price.Price()
        holdings = market.ally.holdings.Holdings()
        long_enter = market.ally.long.enter.get_long(market_price, dry_run)
        long_exit = market.ally.long.exit.get_exit_long(market_price, holdings, dry_run)
        short_enter = market.ally.short.enter.get_short(market_price, dry_run)
        short_exit = market.ally.short.exit.get_exit_short(market_price, holdings, dry_run)

        long_enter_dryrun = market.ally.long.enter.get_long(market_price, True)
        long_exit_dryrun = market.ally.long.exit.get_exit_long(market_price, holdings, True)
        short_enter_dryrun = market.ally.short.enter.get_short(market_price, True)
        short_exit_dryrun = market.ally.short.exit.get_exit_short(market_price, holdings, True)

        self.long_enter = long_enter
        self.long_exit = long_exit
        self.short_enter = short_enter
        self.short_exit = short_exit
        self.long_enter_dryrun = long_enter_dryrun
        self.long_exit_dryrun = long_exit_dryrun
        self.short_enter_dryrun = short_enter_dryrun
        self.short_exit_dryrun = short_exit_dryrun

        symbol_to_strategy = lambda symbol: GapTradeStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit, market.tradier.price.Price(), prev_day_closes)

        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            a_current_time = a_current_time
        )

        strategy.ingestion_run.bar_with_times_ingestion_run.polygon_ingestion_run.if_print_message = False
        PolygonIngestionRun(self, subscription_id)

    def on_gap(self, gap):
        if gap.symbol not in self.strategy_per_symbol:
            self.strategy_per_symbol[gap.symbol] = self.symbol_to_strategy(gap.symbol)
        self.strategy_per_symbol[gap.symbol].on_gap(gap)

    def on_new_timebucket(self):
        for _, strategy in self.strategy_per_symbol.copy().items():
            strategy.on_new_timebucket()
        super().on_new_timebucket()

    def on_daily_trade_start(self):
        super().on_daily_trade_start()
        for _, strategy in self.strategy_per_symbol.items():
            strategy.on_daily_trade_start()

