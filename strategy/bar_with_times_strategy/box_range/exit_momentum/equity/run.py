from strategy.bar_with_times_strategy.box_range.exit_momentum.strategy import BoxRangeExitMomentumTradeStrategy
import util.logging
import util.current_time as current_time
from strategy.factors.box_range.local_extremes import LocalExtremesParameter
from strategy.bar_with_times_strategy.box_range.exit_momentum.strategy import BoxRangeExitMomentumTradeStrategyParameter
import market.ally.util
import market.tradier.util
import market.tdameritrade.util
from strategy.bar_with_times_strategy.run import BarWithTimeTradeStrategyRun
import strategy.ingestion_run.bar_with_times_ingestion_run.polygon_ingestion_run
from strategy.ingestion_run.bar_with_times_ingestion_run.polygon_ingestion_run import PolygonIngestionRun
from enum import Enum
from market.util import get_equity_broker_mode_from_str, EQUITY_BROKER_MODE
import util.symbols

_WINDOW_MINUTE = 15

def get_factor_param():
    param = LocalExtremesParameter(_WINDOW_MINUTE)
    return param

_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 5
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 5
_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 30
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 30
_QUANTITY_WINDOW_MINUTES = 10
_TRADING_VOLUME_UPPER_BOUND_LONG = None
_TRADING_VOLUME_LOWER_BOUND_LONG = 1000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 1000
_PRICE_LOWER_BOUND = 6.0
_PRICE_UPPER_BOUND = 4000.0
_OFF_THRESHOLD = 0.05
_BOX_HEIGHT_RATIO_MAX = 0.10
_BOX_HEIGHT_RATIO_MIN = 0.005

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

class BoxRangeExitMomentumTradeStrategyRun(BarWithTimeTradeStrategyRun):
    def __init__(self, dry_run, positionsize, a_current_time = None, subscription_id = None, equity_broker_mode=EQUITY_BROKER_MODE.TDAMERITRADE):
        util.logging.log_to_std = False

        self.allowed_symbols = set(util.symbols.get_symbols_snp100())

        self.last_tick_epoch_second = 0
        self.current_time = a_current_time if a_current_time else current_time.CurrentTime()
        self.tick_minute_sleep_duration_seconds = 10
        self.positionsize = positionsize

        long_enter = None
        long_exit = None
        short_enter = None
        short_exit = None

        long_enter_dryrun = None
        long_exit_dryrun = None
        short_enter_dryrun = None
        short_exit_dryrun = None

        if equity_broker_mode is EQUITY_BROKER_MODE.ALLY:
            util.logging.info('inintializing for ally broker')
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun = market.ally.util.get_markets(dry_run)

        elif equity_broker_mode is EQUITY_BROKER_MODE.TRADIER:
            util.logging.info('inintializing for tradier broker')
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun = market.tradier.util.get_markets(dry_run)

        elif equity_broker_mode is EQUITY_BROKER_MODE.TDAMERITRADE:
            util.logging.info('inintializing for tdameritrade broker')
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun = market.tdameritrade.util.get_markets(dry_run)

        self.long_enter = long_enter
        self.long_exit = long_exit
        self.short_enter = short_enter
        self.short_exit = short_exit
        self.long_enter_dryrun = long_enter_dryrun
        self.long_exit_dryrun = long_exit_dryrun
        self.short_enter_dryrun = short_enter_dryrun
        self.short_exit_dryrun = short_exit_dryrun

        symbol_to_strategy = lambda symbol: BoxRangeExitMomentumTradeStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit, strategy_param=get_strategy_param(), factor_param=get_factor_param())
        self.strategy_per_symbol = {}

        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            a_current_time = a_current_time
        )

        strategy.ingestion_run.bar_with_times_ingestion_run.polygon_ingestion_run.if_print_message = False
        PolygonIngestionRun(self, subscription_id)


    def on_trade(self, trade):
        if trade.symbol not in self.allowed_symbols:
            return
        super().on_trade(trade)
