from strategy.orderbook_strategy.orderbook_flow.strategy import OrderbookFlowStrategy
import util.logging
import util.current_time as current_time
import market.ally.util
import market.tradier.util
import market.tdameritrade.util
from strategy.orderbook_strategy.run import OrderbookStrategyRun
from strategy.ingestion_run.orderbook_ingestion_run.orderbook_ingestion_run import OrderbookIngestionRun
from market.util import get_equity_broker_mode_from_str, EQUITY_BROKER_MODE

class OrderbookFlowStrategyRun(OrderbookStrategyRun):
    def __init__(self, dry_run, positionsize, a_current_time = None, subscription_id = None, equity_broker_mode=EQUITY_BROKER_MODE.TDAMERITRADE):
        util.logging.log_to_std = False

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

        symbol_to_strategy = lambda symbol: OrderbookFlowStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit)

        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            a_current_time = a_current_time
        )

        OrderbookIngestionRun(self, subscription_id)


