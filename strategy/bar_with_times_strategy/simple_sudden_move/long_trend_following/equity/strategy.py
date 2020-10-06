from strategy.bar_with_times_strategy.simple_sudden_move.long_trend_following.strategy import SimpleSuddenMoveLongTrendFollowingTradeStrategy
from strategy.factors.bar_with_times_factors.simple_sudden_move import SimpleSuddenMove, SimpleSuddenMoveParameter
from strategy.bar_with_times_strategy.simple_sudden_move.strategy import SimpleSuddenMoveTradeStrategyParameter


_CHANGE_THRESHOLD = 0.15
_CHANGE_WINDOW_MINUTE = 15

_STOP_LOSS_THRESHOLD = 0.04
_HARD_STOP_LOSS_THRESHOLD = 0.06
_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 30
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 20
_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 60 * 10
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 60 * 15
_QUANTITY_WINDOW_MINUTES = _CHANGE_WINDOW_MINUTE + 2
_LOCAL_MIN_MAX_WINDOW_SECONDS = 60 * 10
_TRADING_VOLUME_UPPER_BOUND_LONG = None
_TRADING_VOLUME_LOWER_BOUND_LONG = 1000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 1000
_PRICE_LOWER_BOUND = 5.0
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

class SimpleSuddenMoveLongTrendFollowingTradeEquityStrategy(SimpleSuddenMoveLongTrendFollowingTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=None, param=None, factor_param=None):
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=current_time)
        factor_param = factor_param if factor_param else get_factor_param()
        factor_map = {'SuddenMove': SimpleSuddenMove(symbol, self.aggregation, factor_param)}
        self.factor_map = factor_map
        self.param = param if param else get_strategy_param()
