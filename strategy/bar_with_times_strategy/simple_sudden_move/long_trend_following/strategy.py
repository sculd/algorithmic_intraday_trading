import util.logging
import util.time
from strategy.strategy import POSITION_MODE
from strategy.factors.bar_with_times_factors.simple_sudden_move import SIMPLE_SUDDEN_MOVE_MODE
from strategy.factors.bar_with_times_factors.simple_sudden_move import SimpleSuddenMove, SimpleSuddenMoveParameter
from strategy.bar_with_times_strategy.simple_sudden_move.strategy import SimpleSuddenMoveTradeStrategy, SimpleSuddenMoveTradeStrategyParameter


_CHANGE_THRESHOLD = 1.0
_CHANGE_WINDOW_MINUTE = 6

_STOP_LOSS_THRESHOLD = 0.04
_HARD_STOP_LOSS_THRESHOLD = 0.10
_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 30
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 20
_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 60 * 10
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 60 * 15
_QUANTITY_WINDOW_MINUTES = 10
_LOCAL_MIN_MAX_WINDOW_SECONDS = 60 * 10
_TRADING_VOLUME_UPPER_BOUND_LONG = None
_TRADING_VOLUME_LOWER_BOUND_LONG = 1000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 1000
_PRICE_LOWER_BOUND = 1.0
_PRICE_UPPER_BOUND = 200.0

def get_factor_param():
    param = SimpleSuddenMoveParameter(
        _CHANGE_WINDOW_MINUTE,
        _CHANGE_THRESHOLD
    )
    return param

def get_strategy_param():
    param = SimpleSuddenMoveTradeStrategyParameter(
        _STOP_LOSS_THRESHOLD,
        _HARD_STOP_LOSS_THRESHOLD,
        _SHORT_POSITION_TIMEOUT_SECONDS,
        _LONG_POSITION_TIMEOUT_SECONDS,
        _MINIMUM_SHORT_POSITION_HOLD_SECONDS,
        _MINIMUM_LONG_POSITION_HOLD_SECONDS,
        _QUANTITY_WINDOW_MINUTES,
        _LOCAL_MIN_MAX_WINDOW_SECONDS,
        _TRADING_VOLUME_UPPER_BOUND_LONG,
        _TRADING_VOLUME_LOWER_BOUND_LONG,
        _TRADING_VOLUME_UPPER_BOUND_SHORT,
        _TRADING_VOLUME_LOWER_BOUND_SHORT,
        _PRICE_LOWER_BOUND,
        _PRICE_UPPER_BOUND
    )
    return param

class SimpleSuddenMoveLongTrendFollowingTradeStrategy(SimpleSuddenMoveTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None):
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=current_time)
        factor_map = {'SuddenMove': SimpleSuddenMove(symbol, self.aggregation, get_factor_param())}
        self.factor_map = factor_map
        self.param = get_strategy_param()

    def update_position_mode_on_ingest(self):
        market_signal, msg = self.factor_map['SuddenMove'].get()

        new_position_mode = self.position_mode
        dt_str = self._get_datetime_str()
        cp = self._get_close_price()
        current_epoch_seconds = self.current_time.get_current_epoch_seconds()
        min_quantity_minutes = self.aggregation.get_minimal_quantity(self.param.quantity_window_minutes, drop_last=True)

        if new_position_mode is not self.position_mode:
            util.logging.info('position mode change from {f} to {t}'.format(f=self.position_mode, t=new_position_mode))

        if self.position_mode is POSITION_MODE.NO_POSITION:
            if market_signal is SIMPLE_SUDDEN_MOVE_MODE.DROP_SIGNAL:
                if min_quantity_minutes > 0:
                    new_position_mode = POSITION_MODE.LONG_ENTERED
                    self._setup_long_stop_loss()
                else:
                    util.logging.info('signal for long enter is ignored as the min_quantity_minutes is 0 during {m} minutes'.format(m=self.param.quantity_window_minutes))

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
            if cp <= self.short_stop_loss_price and seconds_since_short_position_enter >= self.param.minimum_short_position_hold_seconds:
                util.logging.info("For {symbol}, leaving a short position for crossing the stop loss. short_stop_loss_price: {short_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, short_stop_loss_price=round(self.short_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp <= self.short_hard_stop_loss_price:
                util.logging.info("For {symbol}, leaving a short position for crossing the hard stop loss. short_hard_stop_loss_price: {short_hard_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, short_hard_stop_loss_price=round(self.short_hard_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp >= self.short_stop_loss_reset_price:
                self._setup_short_stop_loss()

        self._update_position_mode(new_position_mode)
        self.prev_market_signal = market_signal
