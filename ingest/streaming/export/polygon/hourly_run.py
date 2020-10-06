import datetime, os
import util.logging as logging
from ingest.streaming.export.daily_aggregation import DailyAggregation
from ingest.streaming.aggregation import BarWithTime, Trade
from ingest.streaming.polygon_run import PolygonAggregationsRun
import ingest.export.equity.export_by_minute, ingest.export.equity.export_raw

TIME_UNIT_SECONDS = 60 * 60


class HourPolygonAggregationsRun(PolygonAggregationsRun):
    def __init__(self, subscription_id = None):
        super().__init__(subscription_id=subscription_id)

    def to_minute_csv_for_past_hour(self):
        epoch_now = int(datetime.datetime.now().timestamp())
        epoch_seconds_end = int(epoch_now // TIME_UNIT_SECONDS) * TIME_UNIT_SECONDS
        epoch_seconds_start = epoch_seconds_end  - TIME_UNIT_SECONDS
        csv_filename = 'polygon_hour_bucket_{f}_{e}.csv'.format(
            f=datetime.datetime.utcfromtimestamp(epoch_seconds_start).strftime('%Y-%m-%dT%H:%M:%S'),
            e=datetime.datetime.utcfromtimestamp(epoch_seconds_end).strftime('%Y-%m-%dT%H:%M:%S')
        )
        full_csv_filename = os.path.join('data', csv_filename)
        self.to_minute_csv(full_csv_filename, epoch_seconds_start=epoch_seconds_start, epoch_seconds_end=epoch_seconds_end)

    def on_trade(self, trade):
        print('[hourly_run.on_trade]')
        if trade.symbol not in self.aggregation_per_symbol:
            self.aggregation_per_symbol[trade.symbol] = DailyAggregation(trade.symbol)
        super().on_trade(trade)
        print('[hourly_run.super().on_trade(trade)] done')
        ingest.export.equity.export_raw.export_trade(trade)

    def on_bar_with_time(self, bar_with_time):
        symbol = bar_with_time.bar.symbol
        if symbol not in self.aggregation_per_symbol:
            self.aggregation_per_symbol[symbol] = DailyAggregation(symbol)
        super().on_bar_with_time(bar_with_time)
        ingest.export.equity.export_by_minute.export_bar_with_time(bar_with_time)

    def to_minute_csv(self, csv_filename, epoch_seconds_start = None, epoch_seconds_end = None):
        logging.info('Aggregations.to_minute_csv for {l_s} symbols'.format(l_s=len(self.aggregation_per_symbol)))
        if len(self.aggregation_per_symbol) == 0:
            return
        with open(csv_filename, 'w') as csv_file:
            csv_file.write(','.join(BarWithTime.get_minute_tuple_names()) + '\n')
            for symbol, aggregation in self.aggregation_per_symbol.copy().items():
                aggregation.append_to_minute_csv(csv_file, epoch_seconds_start=epoch_seconds_start, epoch_seconds_end=epoch_seconds_end)

    def to_rawdata_csv_for_past_hour(self):
        print('[HourPolygonAggregationsRun.to_rawdata_csv_for_past_hour]')
        epoch_now = int(datetime.datetime.now().timestamp())
        epoch_seconds_end = int(epoch_now // TIME_UNIT_SECONDS) * TIME_UNIT_SECONDS
        epoch_seconds_start = epoch_seconds_end  - TIME_UNIT_SECONDS
        csv_filename = 'polygon_rawdata_bucket_{f}_{e}.csv'.format(
            f=datetime.datetime.utcfromtimestamp(epoch_seconds_start).strftime('%Y-%m-%dT%H:%M:%S'),
            e=datetime.datetime.utcfromtimestamp(epoch_seconds_end).strftime('%Y-%m-%dT%H:%M:%S')
        )
        full_csv_filename = os.path.join('data', csv_filename)
        self.to_rawdata_csv(full_csv_filename, epoch_seconds_start=epoch_seconds_start, epoch_seconds_end=epoch_seconds_end)

    def to_rawdata_csv(self, csv_filename, epoch_seconds_start = None, epoch_seconds_end = None):
        logging.info('Aggregations.to_rawdata_csv for {l_s} symbols'.format(l_s=len(self.aggregation_per_symbol)))
        print('[HourPolygonAggregationsRun.to_rawdata_csv]')
        if len(self.aggregation_per_symbol) == 0:
            print('[HourPolygonAggregationsRun.to_rawdata_csv] no appregation')
            return
        with open(csv_filename, 'w') as csv_file:
            csv_file.write(','.join(Trade.get_tuple_names()) + '\n')
            for symbol, aggregation in self.aggregation_per_symbol.copy().items():
                aggregation.append_to_rawdata_csv(csv_file, epoch_seconds_start=epoch_seconds_start, epoch_seconds_end=epoch_seconds_end)

