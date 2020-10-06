from strategy.bar_with_times_strategy.move_stat_collect.strategy import MoveStatCollectStrategy
import util.logging
import util.current_time
import market.ally.long.enter, market.ally.long.exit
import market.ally.short.enter, market.ally.short.exit
import market.ally.holdings
import market.ally.price
from strategy.bar_with_times_strategy.run_csv import BarWithTimeTradeTradeStrategyCsvRun

class MoveStatCollectStrategyCsvRun(BarWithTimeTradeTradeStrategyCsvRun):
    def __init__(self, positionsize, csv_filename):
        symbol_to_strategy = lambda symbol: MoveStatCollectStrategy(self.positionsize, symbol, current_time=mock_current_time)

        mock_current_time = util.current_time.MockCurrentTime(0)

        market_price = market.ally.price.Price()
        holdings = market.ally.holdings.Holdings()
        long_enter = market.ally.long.enter.get_long(market_price, True)
        long_exit = market.ally.long.exit.get_exit_long(market_price, holdings, True)
        short_enter = market.ally.short.enter.get_short(market_price, True)
        short_exit = market.ally.short.exit.get_exit_short(market_price, holdings, True)

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
        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            csv_filename, mock_current_time)

    def on_ingestion_end(self):
        super().on_ingestion_end()

        for _, strategy in self.strategy_per_symbol.items():
            strategy.on_daily_trade_end()

