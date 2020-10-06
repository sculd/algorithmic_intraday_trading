import util.logging
import util.time
from strategy.strategy import POSITION_MODE
from strategy.bar_with_times_strategy.strategy import BarWithTimesTradeStrategy, BarWithTimesTradeStrategyParameter
from strategy.factors.bar_with_times_factors.sudden_move import SuddenMove, SuddenMoveParameter


_CHANGE_THRESHOLD_JUMP = 0.1
_CHANGE_THRESHOLD_DROP = -0.1
_IGNORE_CHANGE_BEYOND_THIS_MAGNITUDE = 0.5
_CHANGE_WINDOW_MINUTE = 10
_CHANGE_WINDOW_MINUTE_SHORT = 5

_STOP_LOSS_THRESHOLD = 0.04
_HARD_STOP_LOSS_THRESHOLD = 0.10
_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 60 * 10
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 60 * 15
_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 30
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 20
_QUANTITY_WINDOW_MINUTES = 10
_SEEKING_ENTRY_EXPIRE_SECONDS = 60 * 20
_LOCAL_MIN_MAX_WINDOW_SECONDS = 60 * 10
_CHANGE_THRESHOLD_FROM_SEEKING_TO_ENTRY = 0.08
_TRADING_VOLUME_UPPER_BOUND_LONG = None
_TRADING_VOLUME_LOWER_BOUND_LONG = 1000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 1000
_PRICE_LOWER_BOUND_LONG = 2.0
_PRICE_LOWER_BOUND_SHORT = 2.0
_PRICE_UPPER_BOUND = 200.0

class SuddenMoveTradeStrategyParameter(BarWithTimesTradeStrategyParameter):
    def __init__(self,
                 stop_loss_threshold,
                 hard_stop_loss_threshold,
                 short_position_timeout_seconds,
                 long_position_timeout_seconds,
                 minimum_short_position_hold_seconds,
                 minimum_long_position_hold_seconds,
                 quantity_window_minutes,
                 seeking_entry_expire_seconds,
                 local_min_max_window_seconds,
                 change_threshold_from_seeking_to_entry_long,
                 change_threshold_from_seeking_to_entry_short,
                 trading_quantity_upper_bound_long,
                 trading_quantity_lower_bound_long,
                 trading_quantity_upper_bound_short,
                 trading_quantity_lower_bound_short,
                 price_lower_bound_long,
                 price_lower_bound_short,
                 price_upper_bound
                 ):
        super().__init__(stop_loss_threshold, hard_stop_loss_threshold, quantity_window_minutes, local_min_max_window_seconds)
        self.short_position_timeout_seconds = short_position_timeout_seconds
        self.long_position_timeout_seconds = long_position_timeout_seconds
        self.minimum_short_position_hold_seconds = minimum_short_position_hold_seconds
        self.minimum_long_position_hold_seconds = minimum_long_position_hold_seconds
        self.quantity_window_minutes = quantity_window_minutes
        self.seeking_entry_expire_seconds = seeking_entry_expire_seconds
        self.local_min_max_window_seconds = local_min_max_window_seconds
        self.change_threshold_from_seeking_to_entry_long = change_threshold_from_seeking_to_entry_long
        self.change_threshold_from_seeking_to_entry_short = change_threshold_from_seeking_to_entry_short
        self.trading_quantity_upper_bound_long = trading_quantity_upper_bound_long
        self.trading_quantity_lower_bound_long = trading_quantity_lower_bound_long
        self.trading_quantity_upper_bound_short = trading_quantity_upper_bound_short
        self.trading_quantity_lower_bound_short = trading_quantity_lower_bound_short
        self.price_lower_bound_long = price_lower_bound_long
        self.price_lower_bound_short = price_lower_bound_short
        self.price_upper_bound = price_upper_bound

def get_strategy_param():
    param = SuddenMoveTradeStrategyParameter(
        _STOP_LOSS_THRESHOLD,
        _HARD_STOP_LOSS_THRESHOLD,
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

class SuddenMoveTradeStrategy(BarWithTimesTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None):
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=current_time)
        self.param = get_strategy_param()
        self.long_count, self.short_count = 0, 0

        factor_map = {'SuddenMove': SuddenMove(symbol, self.aggregation, self.get_factor_param())}
        self.factor_map = factor_map

    def get_factor_param(self):
        param = SuddenMoveParameter(
            _CHANGE_THRESHOLD_JUMP,
            _CHANGE_THRESHOLD_DROP,
            _IGNORE_CHANGE_BEYOND_THIS_MAGNITUDE,
            min(_PRICE_LOWER_BOUND_LONG, _PRICE_LOWER_BOUND_SHORT),
            _CHANGE_WINDOW_MINUTE,
            _CHANGE_WINDOW_MINUTE_SHORT
        )
        return param

    def check_spread_for_seeking_position(self):
        spr = self.long_enter.market_price.get_bidask_spread(self.symbol)
        if abs(spr) > 0.03:
            util.logging.debug("for {symbol} a long term move was observed but the spread is too large. spread (ask - bid) / bid: {spr}, at {t}".format(
                    symbol=self.symbol, spr=spr,
                    t=self.aggregation.get_latest_time()))
            return False
        return True

    def on_new_timebucket(self):
        current_epoch_seconds = self.current_time.get_current_epoch_seconds()
        dt_str = self._get_datetime_str()
        cp = self._get_close_price()

        if self.position_mode is POSITION_MODE.LONG_ENTERED:
            seconds_since_long_position_enter = current_epoch_seconds - self.price_snapshot_long_enter.epoch_seconds
            util.logging.debug('({dt_str}) on_new_timebucket, seconds since entering long for {symbol}: {sec}, price: {cp}, entered: {entered}'.format(
                dt_str=dt_str, symbol=self.symbol, sec=seconds_since_long_position_enter, cp=cp, entered=self.price_snapshot_long_enter.price))
            if seconds_since_long_position_enter >= self.param.long_position_timeout_seconds:
                util.logging.info("For {symbol} leaving a long position for timing out. Seconds since enter: {seconds}".format(
                    symbol = self.symbol,
                    seconds = seconds_since_long_position_enter
                ))
                self._update_position_mode(POSITION_MODE.NO_POSITION)

        if self.position_mode is POSITION_MODE.SHORT_ENTERED:
            seconds_since_short_position_enter = current_epoch_seconds - self.price_snapshot_short_enter.epoch_seconds
            util.logging.debug('({dt_str}) on_new_timebucket, seconds since entering short for {symbol}: {sec}, price: {cp}, entered: {entered}'.format(
                dt_str=dt_str, symbol=self.symbol, sec=seconds_since_short_position_enter, cp=cp, entered=self.price_snapshot_short_enter.price))
            if seconds_since_short_position_enter >= self.param.short_position_timeout_seconds:
                util.logging.info("For {symbol} leaving a short position for timing out. Seconds since enter: {seconds}".format(
                    symbol = self.symbol,
                    seconds = seconds_since_short_position_enter
                ))
                self._update_position_mode(POSITION_MODE.NO_POSITION)
