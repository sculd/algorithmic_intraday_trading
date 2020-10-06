import util.logging
import util.current_time as current_time
from ingest.streaming.aggregation import BarWithTime, Bar
from strategy.ingestion_run.cryptowatch_ingestion_run import CryptowatchIngestionRun
from strategy.bar_publish.strategy import BarPublishStrategy
import publish.influxdb
import threading, time

class CryptoWatchBarPublish:
    def __init__(self, exchange, symbol_to_strategy):
        self.aggregation_per_symbol = {}

        util.logging.log_to_std = False
        self.current_time = current_time.CurrentTime()
        self.tick_minute_sleep_duration_seconds = 10
        self.exchange = exchange
        self.to_strategy = symbol_to_strategy

    def on_bar_with_time(self, bar_with_time):
        if bar_with_time.bar.symbol not in self.aggregation_per_symbol:
            self.aggregation_per_symbol[bar_with_time.bar.symbol] = self.to_strategy(self.exchange, bar_with_time.bar.symbol)
        self.aggregation_per_symbol[bar_with_time.bar.symbol].on_bar_with_time(bar_with_time)

    def on_new_minute(self):
        try:
            for _, aggregation in self.aggregation_per_symbol.items():
                aggregation.on_new_timebucket()
        except Exception as e:
            print(e)

class CryptoWatchBarPublishRun:
    def __init__(self, subscription_id, a_current_time = None):
        self.bar_publish_per_exchange = {}
        self.to_strategy = lambda exchange, symbol: BarPublishStrategy(exchange, symbol)

        CryptowatchIngestionRun(self, subscription_id)
        self._cnt = 0
        self.current_time = a_current_time if a_current_time else current_time.CurrentTime()
        self.last_tick_epoch_second = 0
        self.tick_minute_sleep_duration_seconds = 10
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
        for _, bar_publish in self.bar_publish_per_exchange.items():
            bar_publish.on_new_minute()

    def on_message(self, msg):
        #  {'exchange': 'kraken', 'symbol': 'xlmusd', 'closetime': '1588118820', 'openStr': '0.068769', 'highStr': '0.068769', 'lowStr': '0.068769', 'closeStr': '0.068769', 'volumeBaseStr': '467.24526392', 'volumeQuoteStr': '32.13198955451448'}
        if self._cnt % 1000 == 0:
            print(msg)
        self._cnt += 1

        exchange = msg['exchange']
        if exchange not in self.bar_publish_per_exchange:
            self.bar_publish_per_exchange[exchange] = CryptoWatchBarPublish(exchange, self.to_strategy)
        bar_publish = self.bar_publish_per_exchange[exchange]

        t = BarWithTime.truncate_to_minute(int(msg['closetime']))
        bar = Bar(msg['symbol'], float(msg['openStr']), float(msg['highStr']), float(msg['lowStr']), float(msg['closeStr']), float(msg['volumeQuoteStr']))
        bar_with_time = BarWithTime(t, bar)
        bar_publish.on_bar_with_time(bar_with_time)


