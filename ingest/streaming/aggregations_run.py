import pandas as pd, numpy as np
import datetime, os
import pytz, time, threading
import util.logging as logging
import util.current_time as current_time
from ingest.streaming.aggregation import Aggregation, BarWithTime


class AggregationsRun:
    def __init__(self, a_current_time = None):
        self.daily_trade_started = True
        self.aggregation_per_symbol = {}

        self.current_time = a_current_time if a_current_time else current_time.CurrentTime()
        self.tick_minute_sleep_duration_seconds = 10
        self.last_tick_epoch_second = 0
        threading.Thread(target=self._tick_minute).start()

    def _is_tick_new_minute(self):
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        return epoch_seconds // 60 - self.last_tick_epoch_second // 60 > 0

    def _tick_minute(self):
        while True:
            if self._is_tick_new_minute():
                self.on_new_minute()
                self.last_tick_epoch_second = self.current_time.get_current_epoch_seconds()
            time.sleep(self.tick_minute_sleep_duration_seconds)

    def on_new_minute(self):
        for _, aggregation in self.aggregation_per_symbol.items():
            aggregation.on_new_minute()

    def print_msg(self, msg):
        print('[print_msg]', msg)

    def clean(self):
        self.aggregation_per_symbol = {}

    def on_daily_trade_start(self):
        logging.info('on_daily_trade_start')
        self.daily_trade_started = True
        self.clean()

    def save_daily_df(self, base_dir='data'):
        pass

    def on_daily_trade_end(self, base_dir='data'):
        logging.info('on_daily_trade_end')
        self.daily_trade_started = False

    def on_trade(self, trade):
        if trade.symbol not in self.aggregation_per_symbol:
            self.aggregation_per_symbol[trade.symbol] = Aggregation(trade.symbol)
        self.aggregation_per_symbol[trade.symbol].on_trade(trade)

    def on_bar_with_time(self, bar_with_time):
        symbol = bar_with_time.bar.symbol
        if symbol not in self.aggregation_per_symbol:
            self.aggregation_per_symbol[symbol] = Aggregation(symbol)
        self.aggregation_per_symbol[symbol].on_bar_with_time(bar_with_time)

    def get_status_string(self):
        bars_avg = np.mean(list(map(lambda ag: len(ag.bar_with_times), self.aggregation_per_symbol.values())))
        return 'size of aggregation_per_symbol: {l}, bars_avg: {bars_avg}'.format(
            l = len(self.aggregation_per_symbol),
            bars_avg = bars_avg
        )

    def get_minute_df(self, print_log = True):
        if print_log:
            logging.info('Aggregations.get_minute_df for {l_s} symbols'.format(l_s=len(self.aggregation_per_symbol)))
        df = pd.DataFrame(columns=BarWithTime.get_minute_tuple_names())
        for symbol, aggregation in self.aggregation_per_symbol.items():
            t_1 = datetime.datetime.utcnow()
            df_ = aggregation.get_minute_df()
            t_2 = datetime.datetime.utcnow()
            dt_21 = t_2 - t_1
            logging.info('{s} seconds {ms} microseconds took to get minute_df for symbol {symbol}'.format(
                s=dt_21.seconds, ms=dt_21.microseconds, symbol=symbol))
            df = df.append(df_)
            t_3 = datetime.datetime.utcnow()
            dt_32 = t_3 - t_2
            logging.info('{s} seconds {ms} microseconds took to append for symbol {symbol}'.format(
                s=dt_32.seconds, ms=dt_32.microseconds, symbol=symbol))
        return df.set_index('datetime')
