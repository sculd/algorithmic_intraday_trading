import util.logging
import util.time
from strategy.strategy import POSITION_MODE
from strategy.bar_with_times_strategy.strategy import BarWithTimesTradeStrategy

_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 60 * 10
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 60 * 15
_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 30
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 20
_QUANTITY_WINDOW_MINUTES = 10
_TRADING_VOLUME_UPPER_BOUND_LONG = None
_TRADING_VOLUME_LOWER_BOUND_LONG = 1000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 1000
_PRICE_LOWER_BOUND = 2.0
_PRICE_UPPER_BOUND = 200.0

class BoxRangeTradeStrategyParameter:
    def __init__(self,
                 short_position_timeout_seconds,
                 long_position_timeout_seconds,
                 minimum_short_position_hold_seconds,
                 minimum_long_position_hold_seconds,
                 quantity_window_minutes,
                 trading_quantity_upper_bound_long,
                 trading_quantity_lower_bound_long,
                 trading_quantity_upper_bound_short,
                 trading_quantity_lower_bound_short,
                 price_lower_bound,
                 price_upper_bound
                 ):
        self.short_position_timeout_seconds = short_position_timeout_seconds
        self.long_position_timeout_seconds = long_position_timeout_seconds
        self.minimum_short_position_hold_seconds = minimum_short_position_hold_seconds
        self.minimum_long_position_hold_seconds = minimum_long_position_hold_seconds
        self.quantity_window_minutes = quantity_window_minutes
        self.trading_quantity_upper_bound_long = trading_quantity_upper_bound_long
        self.trading_quantity_lower_bound_long = trading_quantity_lower_bound_long
        self.trading_quantity_upper_bound_short = trading_quantity_upper_bound_short
        self.trading_quantity_lower_bound_short = trading_quantity_lower_bound_short
        self.price_lower_bound = price_lower_bound
        self.price_upper_bound = price_upper_bound

def get_strategy_param():
    param = BoxRangeTradeStrategyParameter(
        _SHORT_POSITION_TIMEOUT_SECONDS,
        _LONG_POSITION_TIMEOUT_SECONDS,
        _MINIMUM_SHORT_POSITION_HOLD_SECONDS,
        _MINIMUM_LONG_POSITION_HOLD_SECONDS,
        _QUANTITY_WINDOW_MINUTES,
        _TRADING_VOLUME_UPPER_BOUND_LONG,
        _TRADING_VOLUME_LOWER_BOUND_LONG,
        _TRADING_VOLUME_UPPER_BOUND_SHORT,
        _TRADING_VOLUME_LOWER_BOUND_SHORT,
        _PRICE_LOWER_BOUND,
        _PRICE_UPPER_BOUND
    )
    return param

class BoxRangeTradeStrategy(BarWithTimesTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None):
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=current_time)
        self.param = get_strategy_param()
        self.long_count, self.short_count = 0, 0

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
