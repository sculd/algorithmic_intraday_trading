from strategy.bar_with_times_strategy.simple_sudden_move.long_trend_reversal.equity.strategy import SimpleSuddenMoveLongTrendReversalTradeEquityStrategy
import util.logging
import util.current_time
import datetime
import market.ally.long.enter, market.ally.long.exit
import market.ally.short.enter, market.ally.short.exit
import market.tdameritrade.holdings
import market.tdameritrade.price
from strategy.bar_with_times_strategy.run_rawdata_csv import BarWithTimeTradeTradeStrategyCsvRun

class SimpleSuddenMoveLongTrendReversalTradeEquityStrategyCsvRun(BarWithTimeTradeTradeStrategyCsvRun):
    def __init__(self, positionsize, csv_filename):
        util.logging.log_to_std = False

        self.last_tick_epoch_second = 0
        self.current_time = util.current_time.MockCurrentTime(0)
        self.tick_minute_sleep_duration_seconds = 10
        self.positionsize = positionsize

        market_price = market.tdameritrade.price.Price()
        holdings = market.tdameritrade.holdings.Holdings()
        long_enter_dryrun = market.ally.long.enter.get_long(market_price, True)
        long_exit_dryrun = market.ally.long.exit.get_exit_long(market_price, holdings, True)
        short_enter_dryrun = market.ally.short.enter.get_short(market_price, True)
        short_exit_dryrun = market.ally.short.exit.get_exit_short(market_price, holdings, True)

        self.long_enter = long_enter_dryrun
        self.long_exit = long_exit_dryrun
        self.short_enter = short_enter_dryrun
        self.short_exit = short_exit_dryrun
        self.long_enter_dryrun = long_enter_dryrun
        self.long_exit_dryrun = long_exit_dryrun
        self.short_enter_dryrun = short_enter_dryrun
        self.short_exit_dryrun = short_exit_dryrun
        mock_current_time = util.current_time.MockCurrentTime(0)

        symbol_to_strategy = lambda symbol: SimpleSuddenMoveLongTrendReversalTradeEquityStrategy(self.positionsize, symbol, self.long_enter, self.long_exit, self.short_enter, self.short_exit, current_time=mock_current_time)

        super().__init__(
            positionsize,
            self.long_enter, self.long_exit, self.short_enter, self.short_exit, self.long_enter_dryrun, self.long_exit_dryrun, self.short_enter_dryrun, self.short_exit_dryrun,
            symbol_to_strategy,
            csv_filename, mock_current_time)

    # override
    def on_trade(self, trade):
        ts = int(trade.timestamp_seconds)
        self.current_time.set_current_epoch_seconds(ts)

        minutes_since_open = (datetime.datetime.utcfromtimestamp(ts).hour - 13) * 60 + (datetime.datetime.utcfromtimestamp(ts).minute - 30)
        if minutes_since_open >= 0:
            self.daily_trade_started = True
        else:
            self.daily_trade_started = False

        if not self.daily_trade_started:
            print('not yet daily trade started', datetime.datetime.utcfromtimestamp(ts), trade)
            return

        super().on_trade(trade)

    # override
    def on_bar_with_time(self, bar_with_time):
        ts = int(bar_with_time.time.timestamp())
        self.current_time.set_current_epoch_seconds(ts)

        minutes_since_open = (datetime.datetime.utcfromtimestamp(ts).hour - 13) * 60 + (datetime.datetime.utcfromtimestamp(ts).minute - 30)
        if minutes_since_open >= 0:
            self.daily_trade_started = True
        else:
            self.daily_trade_started = False

        if not self.daily_trade_started:
            print('not yet daily trade started', datetime.datetime.utcfromtimestamp(ts), bar_with_time)
            return

        super().on_bar_with_time(bar_with_time)

