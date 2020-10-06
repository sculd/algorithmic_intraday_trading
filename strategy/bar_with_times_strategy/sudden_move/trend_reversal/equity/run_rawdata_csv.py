from strategy.bar_with_times_strategy.sudden_move.trend_reversal.equity.strategy import SuddenMoveTrendReversalEquityTradeStrategy
import util.logging
import util.current_time
import market.ally.long.enter, market.ally.long.exit
import market.ally.short.enter, market.ally.short.exit
import market.ally.holdings
import market.ally.price
from strategy.bar_with_times_strategy.run_rawdata_csv import BarWithTimeTradeTradeStrategyCsvRun

class SuddenMoveTrendReversalTradeStrategyCsvRun(BarWithTimeTradeTradeStrategyCsvRun):
    def __init__(self, positionsize, csv_filename):
        util.logging.log_to_std = False

        self.last_tick_epoch_second = 0
        self.current_time = util.current_time.MockCurrentTime(0)
        self.tick_minute_sleep_duration_seconds = 10
        self.positionsize = positionsize

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
        mock_current_time = util.current_time.MockCurrentTime(0)

        symbol_to_strategy = lambda symbol: SuddenMoveTrendReversalEquityTradeStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit, current_time=mock_current_time)

        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            csv_filename, mock_current_time)


