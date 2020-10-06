from strategy.run import TICK_TIMEBUCKET_SECONDS
from strategy.bar_with_times_strategy.run import BarWithTimeTradeStrategyRun
from strategy.ingestion_run.bar_with_times_ingestion_run.csv_ingestion_run import BarWithTimesCsvIngestionRun
import strategy.profit

class BarWithTimeTradeTradeStrategyCsvRun(BarWithTimeTradeStrategyRun):
    def __init__(self, positionsize, long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
                 symbol_to_strategy, csv_filename, mock_current_time):
        super().__init__(
            positionsize,
            long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun,
            symbol_to_strategy,
            a_current_time = mock_current_time,
            to_start_tick_timebucket_thread = False
        )
        self.profit_stat = strategy.profit.ProfitStat(None)

        BarWithTimesCsvIngestionRun(self, csv_filename)

    def _is_tick_new_timebucket_on_timestamp_seconds(self, timestamp_seconds):
        return timestamp_seconds // TICK_TIMEBUCKET_SECONDS - self.last_tick_epoch_second // TICK_TIMEBUCKET_SECONDS > 0

    def _is_timestamp_reset(self, timestamp_seconds):
        return timestamp_seconds - self.last_tick_epoch_second < 0

    def on_bar_with_time(self, bar_with_time):
        ts = int(bar_with_time.time.timestamp())
        self.current_time.set_current_epoch_seconds(ts)
        if bar_with_time.bar.symbol not in self.strategy_per_symbol:
            self.strategy_per_symbol[bar_with_time.bar.symbol] = self.symbol_to_strategy(bar_with_time.bar.symbol)
        self.strategy_per_symbol[bar_with_time.bar.symbol].current_time.set_current_epoch_seconds(ts)

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
