import pandas as pd, numpy as np
import datetime, os, copy
import util.logging as logging
from ingest.streaming.orderbook import OrderbookSnapshots, OrderbookSnapshot
from ingest.streaming.orderbook_run import OrderbookRun

TIME_UNIT_SECONDS = 60 * 60


class HourlyOrderbookRun(OrderbookRun):
    def __init__(self, subscription_id = None):
        super().__init__(subscription_id=subscription_id)
        self.orderbook_snapshots_per_symbol = {}

    def to_csv_for_past_hour(self):
        print('[HourlyOrderbookRun.to_csv_for_past_hour]')
        epoch_now = int(datetime.datetime.now().timestamp())
        epoch_seconds_end = int(epoch_now // TIME_UNIT_SECONDS) * TIME_UNIT_SECONDS
        epoch_seconds_start = epoch_seconds_end  - TIME_UNIT_SECONDS
        csv_filename = 'orderbook_bucket_{f}_{e}.csv'.format(
            f=datetime.datetime.utcfromtimestamp(epoch_seconds_start).strftime('%Y-%m-%dT%H:%M:%S'),
            e=datetime.datetime.utcfromtimestamp(epoch_seconds_end).strftime('%Y-%m-%dT%H:%M:%S')
        )
        full_csv_filename = os.path.join('data', csv_filename)
        self.to_csv(full_csv_filename, epoch_seconds_start=epoch_seconds_start, epoch_seconds_end=epoch_seconds_end)

    def on_update(self, snapshot):
        print('[on_update]', str(snapshot))
        symbol = snapshot.symbol
        if symbol not in self.orderbook_snapshots_per_symbol:
            self.orderbook_snapshots_per_symbol[symbol] = OrderbookSnapshots(symbol)
        self.orderbook_snapshots_per_symbol[symbol].add(snapshot)
        super().on_update(snapshot)

    def to_csv(self, csv_filename, epoch_seconds_start = None, epoch_seconds_end = None):
        logging.info('HourlyOrderbookRun.to_csv for {l_s} symbols'.format(l_s=len(self.orderbook_snapshots_per_symbol)))
        print('[HourlyOrderbookRun.to_csv]')
        if len(self.orderbook_snapshots_per_symbol) == 0:
            return
        with open(csv_filename, 'w') as csv_file:
            csv_file.write(','.join(OrderbookSnapshot.get_tuple_names()) + '\n')
            for symbol, snapshots in self.orderbook_snapshots_per_symbol.copy().items():
                snapshots.append_to_csv_file(csv_file, epoch_seconds_start=epoch_seconds_start, epoch_seconds_end=epoch_seconds_end)

