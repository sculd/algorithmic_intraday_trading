from strategy.bar_with_times_strategy.box_range.exit_momentum.strategy import BoxRangeExitMomentumTradeStrategy
import util.logging
import util.current_time
from strategy.bar_with_times_strategy.box_range.exit_momentum.equity.run import get_factor_param, get_strategy_param
import market.ally.long.enter, market.ally.long.exit
import market.ally.short.enter, market.ally.short.exit
import market.ally.holdings
import market.ally.price
import datetime
from strategy.bar_with_times_strategy.run_rawdata_csv import BarWithTimeTradeTradeStrategyCsvRun
import util.symbols


class BoxRangeExitMomentumTradeStrategyCsvRun(BarWithTimeTradeTradeStrategyCsvRun):
    def __init__(self, positionsize, csv_filename):
        util.logging.log_to_std = True

        self.allowed_symbols = set(util.symbols.get_symbols_snp100())

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

        symbol_to_strategy = lambda symbol: BoxRangeExitMomentumTradeStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit, current_time=mock_current_time, strategy_param=get_strategy_param(), factor_param=get_factor_param())

        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            csv_filename, mock_current_time)

    # override
    def on_trade(self, trade):
        if trade.symbol not in self.allowed_symbols:
            return
        self.current_time.set_current_epoch_seconds(trade.timestamp_seconds)

        minutes_since_open = (datetime.datetime.utcfromtimestamp(trade.timestamp_seconds).hour - 13) * 60 + (datetime.datetime.utcfromtimestamp(trade.timestamp_seconds).minute - 30)
        if minutes_since_open >= 0:
            self.daily_trade_started = True

        if not self.daily_trade_started:
            print('not yet daily trade started', datetime.datetime.utcfromtimestamp(trade.timestamp_seconds), trade)
            return

        super().on_trade(trade)

