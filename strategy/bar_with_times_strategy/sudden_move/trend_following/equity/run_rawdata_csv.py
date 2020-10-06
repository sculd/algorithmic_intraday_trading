from strategy.bar_with_times_strategy.sudden_move.trend_following.equity.strategy import SuddenMoveTrendFollowingEquityTradeStrategy
from strategy.factors.bar_with_times_factors.sudden_move import SuddenMoveParameter
from strategy.bar_with_times_strategy.sudden_move.strategy import SuddenMoveTradeStrategyParameter
import datetime
import util.logging
import util.current_time
import market.ally.long.enter, market.ally.long.exit
import market.ally.short.enter, market.ally.short.exit
import market.ally.holdings
import market.ally.price
from strategy.bar_with_times_strategy.run_rawdata_csv import BarWithTimeTradeTradeStrategyCsvRun

_CHANGE_THRESHOLD_JUMP = 0.05
_CHANGE_THRESHOLD_DROP = -0.05
_CHANGE_THRESHOLD_FROM_SEEKING_TO_ENTRY = 0.08
_IGNORE_CHANGE_BEYOND_THIS_MAGNITUDE = 3.0
_PRICE_LOWER_BOUND_LONG = 0.1
_PRICE_LOWER_BOUND_SHORT = 6.0
_CHANGE_WINDOW_MINUTE = 4
_CHANGE_WINDOW_MINUTE_SHORT = 1

def get_factor_param():
    param = SuddenMoveParameter(
        _CHANGE_THRESHOLD_JUMP,
        _CHANGE_THRESHOLD_DROP,
        _IGNORE_CHANGE_BEYOND_THIS_MAGNITUDE,
        min(_PRICE_LOWER_BOUND_LONG, _PRICE_LOWER_BOUND_SHORT),
        _CHANGE_WINDOW_MINUTE,
        _CHANGE_WINDOW_MINUTE_SHORT
    )
    return param

_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 4
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 4
_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 60 * 2
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 60 * 2
_QUANTITY_WINDOW_MINUTES = 10
_SEEKING_ENTRY_EXPIRE_SECONDS = 60 * 20
_LOCAL_MIN_MAX_WINDOW_SECONDS = 60 * 10
_PRICE_UPPER_BOUND = 100.0
_TRADING_VOLUME_UPPER_BOUND_LONG = 300000
_TRADING_VOLUME_LOWER_BOUND_LONG = 50000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 100000

def get_strategy_param():
    param = SuddenMoveTradeStrategyParameter(
        _SHORT_POSITION_TIMEOUT_SECONDS,
        _LONG_POSITION_TIMEOUT_SECONDS,
        _MINIMUM_SHORT_POSITION_HOLD_SECONDS,
        _MINIMUM_LONG_POSITION_HOLD_SECONDS,
        _QUANTITY_WINDOW_MINUTES,
        _SEEKING_ENTRY_EXPIRE_SECONDS,
        _LOCAL_MIN_MAX_WINDOW_SECONDS,
        _CHANGE_THRESHOLD_FROM_SEEKING_TO_ENTRY,
        -1 * _CHANGE_THRESHOLD_FROM_SEEKING_TO_ENTRY,
        _TRADING_VOLUME_UPPER_BOUND_LONG,
        _TRADING_VOLUME_LOWER_BOUND_LONG,
        _TRADING_VOLUME_UPPER_BOUND_SHORT,
        _TRADING_VOLUME_LOWER_BOUND_SHORT,
        _PRICE_LOWER_BOUND_LONG,
        _PRICE_LOWER_BOUND_SHORT,
        _PRICE_UPPER_BOUND
    )
    return param

class SuddenMoveTrendFollowingTradeStrategyCsvRun(BarWithTimeTradeTradeStrategyCsvRun):
    def __init__(self, positionsize, csv_filename):
        util.logging.log_to_std = True

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

        symbol_to_strategy = lambda symbol: SuddenMoveTrendFollowingEquityTradeStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit, current_time=mock_current_time, param=get_strategy_param(), factor_param=get_factor_param())

        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            csv_filename, mock_current_time)

    # override
    def on_trade(self, trade):
        self.current_time.set_current_epoch_seconds(trade.timestamp_seconds)

        minutes_since_open = (datetime.datetime.utcfromtimestamp(trade.timestamp_seconds).hour - 13) * 60 + (datetime.datetime.utcfromtimestamp(trade.timestamp_seconds).minute - 30)
        if minutes_since_open >= 0:
            self.daily_trade_started = True

        if not self.daily_trade_started:
            print('not yet daily trade started', datetime.datetime.utcfromtimestamp(trade.timestamp_seconds), trade)
            return

        super().on_trade(trade)

