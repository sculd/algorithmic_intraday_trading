from ingest.streaming.aggregation import Aggregation, BAR_WITH_TIME_COMBINE_MODE
from google.cloud import pubsub_v1
import publish.influxdb

_publisher = None
def _get_publisher():
    global _publisher
    if _publisher is None:
        _publisher = pubsub_v1.PublisherClient()
    return _publisher

class BarPublishStrategy(Aggregation):
    def __init__(self, exchange, symbol):
        super().__init__(symbol, bar_with_time_combine_mode = BAR_WITH_TIME_COMBINE_MODE.REPLACE)
        self.exchange = exchange

    def on_new_timebucket(self):
        cp = self._get_close_price()

        tags = {
            'exchange': self.exchange,
            'symbol': self.symbol
        }
        fields = {
            'close': cp
        }
        print('publish to influxdb', tags, fields)
        publish.influxdb.publish('timeseries', tags, fields)

    def on_bar_with_time(self, new_bar_with_time):
        super().on_bar_with_time(new_bar_with_time)

