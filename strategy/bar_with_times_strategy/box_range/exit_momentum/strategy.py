import util.logging
import util.time
from strategy.strategy import POSITION_MODE
from strategy.factors.box_range.local_extremes import LocalExtremesFactor, LocalExtremesParameter
from strategy.bar_with_times_strategy.box_range.strategy import BoxRangeTradeStrategy, BoxRangeTradeStrategyParameter


_CHANGE_THRESHOLD_JUMP = 0.15
_CHANGE_THRESHOLD_DROP = -0.15
_IGNORE_CHANGE_BEYOND_THIS_MAGNITUDE = 7.0
_PRICE_LOWER_BOUND = 5.0
_PRICE_UPPER_BOUND = 200.0
_CHANGE_WINDOW_MINUTE = 10
_CHANGE_WINDOW_MINUTE_SHORT = 5

_WINDOW_MINUTE = 3

def get_factor_param():
    param = LocalExtremesParameter(_WINDOW_MINUTE)
    return param


class BoxRangeExitMomentumTradeStrategyParameter(BoxRangeTradeStrategyParameter):
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
                 price_upper_bound,
                 off_threshold,
                 box_height_ratio_max,
                 box_height_ratio_min
                 ):
        super().__init__(
            short_position_timeout_seconds, long_position_timeout_seconds, minimum_short_position_hold_seconds, minimum_long_position_hold_seconds, quantity_window_minutes, trading_quantity_upper_bound_long, trading_quantity_lower_bound_long, trading_quantity_upper_bound_short, trading_quantity_lower_bound_short, price_lower_bound, price_upper_bound
        )
        self.off_threshold = off_threshold
        self.box_height_ratio_max = box_height_ratio_max
        self.box_height_ratio_min = box_height_ratio_min

_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 5
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 5
_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 30
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 30
_QUANTITY_WINDOW_MINUTES = 10
_TRADING_VOLUME_UPPER_BOUND_LONG = None
_TRADING_VOLUME_LOWER_BOUND_LONG = 1000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 1000
_OFF_THRESHOLD = 0.05
_BOX_HEIGHT_RATIO_MAX = 0.2
_BOX_HEIGHT_RATIO_MIN = 0.02

def get_strategy_param():
    param = BoxRangeExitMomentumTradeStrategyParameter(
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
        _PRICE_UPPER_BOUND,
        _OFF_THRESHOLD,
        _BOX_HEIGHT_RATIO_MAX,
        _BOX_HEIGHT_RATIO_MIN
    )
    return param

class BoxRangeExitMomentumTradeStrategy(BoxRangeTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None, strategy_param = None, factor_param = None):
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=current_time)
        factor_param = factor_param if factor_param else get_factor_param()
        factor_map = {'LocalExtremes': LocalExtremesFactor(symbol, self.aggregation.bar_with_times, factor_param, current_time=current_time)}
        self.factor_map = factor_map
        strategy_param = strategy_param if strategy_param else get_strategy_param()
        self.param = strategy_param

    # override
    def on_trade(self, trade):
        self.aggregation.on_trade(trade)
        self.factor_map['LocalExtremes'].on_trade(trade)
        self.on_ingest()

    def update_position_mode_on_ingest(self):
        new_position_mode = self.position_mode

        dt_str = self._get_datetime_str()
        upper, lower = self.factor_map['LocalExtremes'].get()
        cp = self._get_close_price()
        if cp < self.param.price_lower_bound:
            return
        if self.param.box_height_ratio_max is not None and (upper - lower) / lower > self.param.box_height_ratio_max:
            return
        if self.param.box_height_ratio_min is not None and (upper - lower) / lower < self.param.box_height_ratio_min:
            return
        current_epoch_seconds = self.current_time.get_current_epoch_seconds()

        if new_position_mode is not self.position_mode:
            util.logging.info('position mode change from {f} to {t}'.format(f=self.position_mode, t=new_position_mode))

        if self.position_mode is POSITION_MODE.NO_POSITION:
            if cp >= upper * (1.0 - self.param.off_threshold):
                util.logging.info('{dt_str} near (below) the upper bound of the box, price: {cp}, upper: {upper}, lower: {lower}, breaking: {breaking}'.format(dt_str=dt_str, cp=cp, upper=upper, lower=lower, breaking=upper * (1.0 - 0.05)))
                new_position_mode = POSITION_MODE.LONG_ENTERED
                self._setup_short_stop_loss()

            elif cp <= lower * (1.0 + self.param.off_threshold):
                util.logging.info('{dt_str} near (above) the lower bound of the box, price: {cp}, upper: {upper}, lower: {lower}, breaking: {breaking}'.format(dt_str=dt_str, cp=cp, upper=upper, lower=lower, breaking=upper * (1.0 + 0.05)))
                new_position_mode = POSITION_MODE.SHORT_ENTERED
                self._setup_long_stop_loss()

        elif self.position_mode is POSITION_MODE.LONG_ENTERED:
            seconds_since_long_position_enter = current_epoch_seconds - self.price_snapshot_long_enter.epoch_seconds
            if cp <= self.long_stop_loss_price and seconds_since_long_position_enter >= self.param.minimum_long_position_hold_seconds:
                util.logging.info("For {symbol}, leaving a long position for crossing the stop loss. long_stop_loss_price: {long_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, long_stop_loss_price=round(self.long_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp <= self.long_hard_stop_loss_price:
                util.logging.info("For {symbol}, leaving a long position for crossing the hard stop loss. long_hard_stop_loss_price: {long_hard_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, long_hard_stop_loss_price=round(self.long_hard_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp >= self.long_stop_loss_reset_price:
                self._setup_long_stop_loss()

        elif self.position_mode is POSITION_MODE.SHORT_ENTERED:
            seconds_since_short_position_enter = current_epoch_seconds - self.price_snapshot_short_enter.epoch_seconds
            if cp >= self.short_stop_loss_price and seconds_since_short_position_enter >= self.param.minimum_short_position_hold_seconds:
                util.logging.info("For {symbol}, leaving a short position for crossing the stop loss. short_stop_loss_price: {short_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, short_stop_loss_price=round(self.short_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp >= self.short_hard_stop_loss_price:
                util.logging.info("For {symbol}, leaving a short position for crossing the hard stop loss. short_hard_stop_loss_price: {short_hard_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, short_hard_stop_loss_price=round(self.short_hard_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp <= self.short_stop_loss_reset_price:
                self._setup_short_stop_loss()


        self._update_position_mode(new_position_mode)
