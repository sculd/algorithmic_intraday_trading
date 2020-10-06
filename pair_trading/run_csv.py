from strategy.run import TICK_TIMEBUCKET_SECONDS
from strategy.bar_with_times_strategy.run import BarWithTimeTradeStrategyRun
from strategy.bar_with_times_strategy.strategy import BarWithTimesTradeStrategy
from strategy.ingestion_run.bar_with_times_ingestion_run.csv_ingestion_run import BarWithTimesCsvIngestionRun
from strategy.bar_with_times_strategy.run_csv import BarWithTimeTradeTradeStrategyCsvRun
from pair_trading.pair import Pair
import strategy.profit
import logging

class PairTradingCsvRun(BarWithTimeTradeTradeStrategyCsvRun):
    def __init__(self, positionsize, long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
                 symbol_to_strategy, csv_filename, mock_current_time, pairs):
        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy, csv_filename, mock_current_time
        )
        self.profit_stat = strategy.profit.ProfitStat(None)

        # validation
        self.symbols = set()
        for pair in pairs:
            if pair[0] in self.symbols or pair[1] in self.symbols:
                logging.error("{s1} or {s2} is already in another pair".format(s1=pair[0], s2=pair[1]))

        self.pair_per_symbol = {}
        for pair in pairs:
            # quote, base, target_ratio
            symbol_quote, symbol_base = pair[0], pair[1]
            strategy_quote = BarWithTimesTradeStrategy(positionsize, symbol_quote, long_enter, long_exit, short_enter, short_exit, mock_current_time)
            strategy_base = BarWithTimesTradeStrategy(positionsize, symbol_base, long_enter, long_exit, short_enter, short_exit, mock_current_time)
            target_ratio = pairs[2]
            self.pair_per_symbol[symbol_quote] = Pair(strategy_quote, strategy_base, target_ratio)
            self.pair_per_symbol[symbol_base] = self.pair_per_symbol[symbol_quote]

        BarWithTimesCsvIngestionRun(self, csv_filename)

    def _is_tick_new_timebucket_on_timestamp_seconds(self, timestamp_seconds):
        return timestamp_seconds // TICK_TIMEBUCKET_SECONDS - self.last_tick_epoch_second // TICK_TIMEBUCKET_SECONDS > 0

    def _is_timestamp_reset(self, timestamp_seconds):
        return timestamp_seconds - self.last_tick_epoch_second < 0

    def on_bar_with_time(self, bar_with_time):
        if bar_with_time.bar.symbol not in self.symbols:
            return
        ts = int(bar_with_time.time.timestamp())
        self.current_time.set_current_epoch_seconds(ts)

        super().on_bar_with_time(bar_with_time)
        if self._is_tick_new_timebucket_on_timestamp_seconds(ts):
            print('csv run, new minute: {t}'.format(t=bar_with_time.time))
        self._on_timestamp_seconds(ts)

    def _on_timestamp_seconds(self, timestamp_seconds):
        if self._is_tick_new_timebucket_on_timestamp_seconds(timestamp_seconds):
            self.on_new_timebucket()
            self.last_tick_epoch_second = timestamp_seconds
        elif self._is_timestamp_reset(timestamp_seconds):
            self.last_tick_epoch_second = timestamp_seconds

    def on_ingestion_end(self):
        for symbol, strategy in self.strategy_per_symbol.items():
            self.profit_stat.union(strategy.profit_stat)
        print('csv run is done:')
        print(str(self.profit_stat))
        self.profit_stat.print_records()
        self.profit_stat.print_cumulative_profit()
