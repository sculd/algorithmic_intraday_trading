import util.logging
import util.current_time as current_time
from ingest.streaming.aggregation import BarWithTime, Bar
from strategy.ingestion_run.cryptowatch_ingestion_run import CryptowatchIngestionRun
from strategy.bar_with_times_strategy.sudden_move.publish_strategy import SuddenMovePublishStrategy

class CryptoWatchSignalPublish:
    def __init__(self, symbol_to_strategy):
        self.aggregation_per_symbol = {}

        util.logging.log_to_std = False
        self.current_time = current_time.CurrentTime()
        self.last_tick_epoch_second = 0
        self.tick_minute_sleep_duration_seconds = 10
        self.symbol_to_strategy = symbol_to_strategy

    def on_bar_with_time(self, bar_with_time):
        if bar_with_time.bar.symbol not in self.aggregation_per_symbol:
            self.aggregation_per_symbol[bar_with_time.bar.symbol] = self.symbol_to_strategy(bar_with_time.bar.symbol)
        self.aggregation_per_symbol[bar_with_time.bar.symbol].on_bar_with_time(bar_with_time)


class CryptoWatchSignalPublishRun:
    def __init__(self, subscription_id, publish_topic):
        self.signal_publish_per_exchange = {}
        self.symbol_to_strategy = lambda symbol: SuddenMovePublishStrategy(symbol, publish_topic)

        CryptowatchIngestionRun(self, subscription_id)
        self._cnt = 0

    def on_message(self, msg):
        #  {'exchange': 'kraken', 'symbol': 'xlmusd', 'closetime': '1588118820', 'openStr': '0.068769', 'highStr': '0.068769', 'lowStr': '0.068769', 'closeStr': '0.068769', 'volumeBaseStr': '467.24526392', 'volumeQuoteStr': '32.13198955451448'}
        if self._cnt % 1000 == 0:
            print(msg)
        self._cnt += 1
        if msg['exchange'] not in self.signal_publish_per_exchange:
            self.signal_publish_per_exchange[msg['exchange']] = CryptoWatchSignalPublish(self.symbol_to_strategy)
        signal_publish = self.signal_publish_per_exchange[msg['exchange']]

        t = BarWithTime.truncate_to_minute(int(msg['closetime']))
        bar = Bar(msg['symbol'], float(msg['openStr']), float(msg['highStr']), float(msg['lowStr']), float(msg['closeStr']), float(msg['volumeQuoteStr']))
        bar_with_time = BarWithTime(t, bar)
        signal_publish.on_bar_with_time(bar_with_time)
