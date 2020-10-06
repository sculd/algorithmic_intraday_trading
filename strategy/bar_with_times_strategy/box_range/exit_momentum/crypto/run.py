from strategy.bar_with_times_strategy.box_range.exit_momentum.strategy import BoxRangeExitMomentumTradeStrategy
from strategy.bar_with_times_strategy.box_range.exit_momentum.strategy import BoxRangeExitMomentumTradeStrategyParameter
import util.logging
import util.current_time as current_time
from strategy.factors.box_range.local_extremes import LocalExtremesParameter
import market.binance.margin_spot.long.enter, market.binance.margin_spot.long.exit
import market.binance.margin_spot.short.enter, market.binance.margin_spot.short.exit
import market.binance.holdings
import market.binance.margin.holdings
import market.binance.price
from strategy.bar_with_times_strategy.run import BarWithTimeTradeStrategyRun
from strategy.ingestion_run.bar_with_times_ingestion_run.binance_ingestion_run import BinanceIngestionRun


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
_PRICE_LOWER_BOUND = 0.1
_PRICE_UPPER_BOUND = 100000.0
_OFF_THRESHOLD = 0.05
_BOX_HEIGHT_RATIO_MAX = 0.2
_BOX_HEIGHT_RATIO_MIN = 0.01

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
    def __init__(self, dry_run, positionsize, a_current_time = None, subscription_id = None):
        util.logging.log_to_std = False

        self.last_tick_epoch_second = 0
        self.current_time = a_current_time if a_current_time else current_time.CurrentTime()
        self.tick_minute_sleep_duration_seconds = 10
        self.positionsize = positionsize

        market_price = market.binance.price.Price()
        holdings = market.binance.holdings.Holdings()
        holdings_margin = market.binance.margin.holdings.MarginHoldings()
        long_enter = market.binance.margin_spot.long.enter.get_long(market_price, dry_run)
        long_exit = market.binance.margin_spot.long.exit.get_exit_long(market_price, holdings, dry_run)
        short_enter = market.binance.margin_spot.short.enter.get_short(market_price, dry_run)
        short_exit = market.binance.margin_spot.short.exit.get_exit_short(market_price, holdings_margin, dry_run)

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

        symbol_to_strategy = lambda symbol: BoxRangeExitMomentumTradeStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit, strategy_param=get_strategy_param(), factor_param=get_factor_param())
        self.strategy_per_symbol = {}

        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            a_current_time = a_current_time
        )

        BinanceIngestionRun(self, subscription_id)


