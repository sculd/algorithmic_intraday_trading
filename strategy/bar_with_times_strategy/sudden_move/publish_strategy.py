import util.logging
import util.time
from ingest.streaming.aggregation import Aggregation, BAR_WITH_TIME_COMBINE_MODE
from strategy.factors.bar_with_times_factors.simple_sudden_move import SimpleSuddenMove, SimpleSuddenMoveParameter, SIMPLE_SUDDEN_MOVE_MODE
from google.cloud import pubsub_v1
import publish.pubsub

_publisher = None
def _get_publisher():
    global _publisher
    if _publisher is None:
        _publisher = pubsub_v1.PublisherClient()
    return _publisher

class SuddenMovePublishStrategy(Aggregation):
    def __init__(self, symbol, publish_topic):
        super().__init__(symbol, bar_with_time_combine_mode = BAR_WITH_TIME_COMBINE_MODE.REPLACE)
        self.publish_topic = publish_topic
        self.factor_map = {}
        self.minutes = [10, 20, 30, 60, 120, 180]
        self.changes = [0.05, 0.1, 0.2, 0.5]
        for minute in self.minutes:
            for change in self.changes:
                self.factor_map['{m},{c}'.format(m=minute, c=change)] = SimpleSuddenMove(symbol, self, SimpleSuddenMoveParameter(minute, change))
        self.prev_simple_sudden_move_modes = {}

    def on_new_timebucket(self):
        pass

    def publish(self, msg):
        publish.pubsub.publish(self.publish_topic, msg)

    def on_bar_with_time(self, new_bar_with_time):
        super().on_bar_with_time(new_bar_with_time)
        for minute in self.minutes:
            for change in self.changes:
                key = '{m},{c}'.format(m=minute, c=change)
                simple_sudden_move, msg = self.factor_map[key].get()
                if simple_sudden_move is not SIMPLE_SUDDEN_MOVE_MODE.NO_SIGNAL:
                    if key not in self.prev_simple_sudden_move_modes or simple_sudden_move is not self.prev_simple_sudden_move_modes[key]:
                        util.logging.info('simple sudden move observed. key: {k} move: {m}'.format(k=key, m=simple_sudden_move))
                        self.publish(msg)

                self.prev_simple_sudden_move_modes[key] = simple_sudden_move

