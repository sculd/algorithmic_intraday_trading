from strategy.bar_with_times_strategy.sudden_move.trend_reversal.strategy import SuddenMoveTrendReversalTradeStrategy
from strategy.factors.bar_with_times_factors.sudden_move import SuddenMove, SuddenMoveParameter
from strategy.bar_with_times_strategy.sudden_move.strategy import SuddenMoveTradeStrategyParameter


_CHANGE_THRESHOLD_JUMP = 0.20
_CHANGE_THRESHOLD_DROP = -0.20
_CHANGE_THRESHOLD_FROM_SEEKING_TO_ENTRY = 0.05
_IGNORE_CHANGE_BEYOND_THIS_MAGNITUDE = 10.0
_PRICE_LOWER_BOUND_LONG = 0.5
_PRICE_LOWER_BOUND_SHORT = 6.0
_PRICE_UPPER_BOUND = 200.0
_CHANGE_WINDOW_MINUTE = 15
_CHANGE_WINDOW_MINUTE_SHORT = 7

_STOP_LOSS_THRESHOLD = 0.04
_HARD_STOP_LOSS_THRESHOLD = 0.08
_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 30
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 20
_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 60 * 10
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 60 * 15
_QUANTITY_WINDOW_MINUTES = 10
_SEEKING_ENTRY_EXPIRE_SECONDS = 60 * 30
_LOCAL_MIN_MAX_WINDOW_SECONDS = 60 * 10
_TRADING_VOLUME_UPPER_BOUND_LONG = 300000
_TRADING_VOLUME_LOWER_BOUND_LONG = 10000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 10000

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

class SuddenMoveTrendReversalEquityTradeStrategy(SuddenMoveTrendReversalTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=None, param=None):
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=current_time)
        factor_map = {'SuddenMove': SuddenMove(symbol, self.aggregation, get_factor_param())}
        self.factor_map = factor_map
        self.param = param if param else get_strategy_param()
