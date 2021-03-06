from strategy.bar_with_times_strategy.timeseries_analysis.trend_reserval.crypto.strategy import SuddenMoveTrendReversalCryptoTradeStrategy
import util.logging
import util.current_time
import market.binance.margin_spot.long.enter, market.binance.margin_spot.long.exit
import market.binance.margin_spot.short.enter, market.binance.margin_spot.short.exit
import market.binance.holdings
import market.binance.margin.holdings
import market.binance.price
from strategy.bar_with_times_strategy.run import BarWithTimeTradeStrategyRun
from strategy.ingestion_run.bar_with_times_ingestion_run.binance_ingestion_run import BinanceIngestionRun


class SuddenMoveTrendReversalTradeStrategyRun(BarWithTimeTradeStrategyRun):
    def __init__(self, dry_run, positionsize, a_current_time = None, subscription_id = None):
        util.logging.log_to_std = False

        self.last_tick_epoch_second = 0
        self.current_time = a_current_time if a_current_time else util.current_time.CurrentTime()
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

        self.strategy_per_symbol = {}

        symbol_to_strategy = lambda symbol: SuddenMoveTrendReversalCryptoTradeStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit, current_time = a_current_time)
        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            a_current_time = a_current_time
        )

        BinanceIngestionRun(self, subscription_id)


