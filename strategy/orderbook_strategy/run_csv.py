from strategy.orderbook_strategy.run import OrderbookStrategyRun
from strategy.ingestion_run.orderbook_ingestion_run.orderbook_csv_ingestion_run import OrerbookCsvIngestionRun
import strategy.profit
import datetime

class OrderbookStrategyCsvRun(OrderbookStrategyRun):
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

        OrerbookCsvIngestionRun(self, csv_filename)

    def _is_tick_new_timebucket_on_timestamp_seconds(self, timestamp_seconds):
        return timestamp_seconds // 60 - self.last_tick_epoch_second // 60 > 0

    def _is_timestamp_reset(self, timestamp_seconds):
        return timestamp_seconds // 60 - self.last_tick_epoch_second // 60 < 0

    def on_orderbook_snapshot(self, orderbook_snapshot):
        ts = int(orderbook_snapshot.epoch_seconds)
        self.current_time.set_current_epoch_seconds(ts)

        symbol = orderbook_snapshot.symbol
        if symbol not in self.strategy_per_symbol:
            self.strategy_per_symbol[symbol] = self.symbol_to_strategy(symbol)
        super().on_orderbook_snapshot(orderbook_snapshot)
        self.strategy_per_symbol[symbol].on_orderbook_snapshot(orderbook_snapshot)

        if self._is_tick_new_timebucket_on_timestamp_seconds(ts):
            print('csv run, new minute: {t}'.format(t=datetime.datetime.utcfromtimestamp(ts)))
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
