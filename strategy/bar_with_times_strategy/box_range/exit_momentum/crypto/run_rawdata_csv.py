from strategy.bar_with_times_strategy.box_range.exit_momentum.strategy import BoxRangeExitMomentumTradeStrategy
from strategy.bar_with_times_strategy.box_range.exit_momentum.strategy import BoxRangeExitMomentumTradeStrategyParameter
import util.logging
import util.current_time
from strategy.factors.box_range.local_extremes import LocalExtremesParameter
import market.binance.margin_spot.long.enter, market.binance.margin_spot.long.exit
import market.binance.margin_spot.short.enter, market.binance.margin_spot.short.exit
import market.binance.holdings
import market.binance.margin.holdings
import market.binance.price
from strategy.bar_with_times_strategy.run_rawdata_csv import BarWithTimeTradeTradeStrategyCsvRun
from strategy.bar_with_times_strategy.box_range.exit_momentum.crypto.run import get_strategy_param, get_factor_param


class BoxRangeExitMomentumTradeStrategyCsvRun(BarWithTimeTradeTradeStrategyCsvRun):
    def __init__(self, positionsize, csv_filename):
        util.logging.log_to_std = True

        self.last_tick_epoch_second = 0
        self.current_time = util.current_time.MockCurrentTime(0)
        self.tick_minute_sleep_duration_seconds = 10
        self.positionsize = positionsize

        market_price = market.binance.price.Price()
        holdings = market.binance.holdings.Holdings()
        holdings_margin = market.binance.margin.holdings.MarginHoldings()
        long_enter = market.binance.margin_spot.long.enter.get_long(market_price, True)
        long_exit = market.binance.margin_spot.long.exit.get_exit_long(market_price, holdings, True)
        short_enter = market.binance.margin_spot.short.enter.get_short(market_price, True)
        short_exit = market.binance.margin_spot.short.exit.get_exit_short(market_price, holdings_margin, True)

        long_enter_dryrun = market.binance.margin_spot.long.enter.get_long(market_price, True)
        long_exit_dryrun = market.binance.margin_spot.long.exit.get_exit_long(market_price, holdings, True)
        short_enter_dryrun = market.binance.margin_spot.short.enter.get_short(market_price, True)
        short_exit_dryrun = market.binance.margin_spot.short.exit.get_exit_short(market_price, holdings_margin, True)

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
        self.daily_trade_started = True
        self.current_time.set_current_epoch_seconds(trade.timestamp_seconds)
        super().on_trade(trade)

