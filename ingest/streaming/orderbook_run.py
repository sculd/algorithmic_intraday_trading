import json, os
from google.cloud import pubsub_v1
from pytz import timezone
from threading import Thread
import util.logging as logging
from ingest.streaming.orderbook import OrderbookSnapshot

def run_loop(orderbook_run, subscription_id):
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_id
    )

    def callback(message):
        msg = json.loads(message.data.decode('utf-8'))
        message.ack()
        on_message(orderbook_run, msg)

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print("Listening for messages on {}\n".format(subscription_path))

    try:
        streaming_pull_future.result()
    except Exception as ex:  # noqa
        logging.error(ex)
        streaming_pull_future.cancel()

def _msg_to_snapshot_list(msg):
    if 'content' not in msg:
        raise Exception('"{key}" field not present in the message: {msg}'.format(key='content', msg=msg))

    snapshot_list = []

    content = msg['content']
    for c in content:
        symbol = c['key']
        snapshot = OrderbookSnapshot(symbol)
        snapshot.epoch_seconds = int(c['BOOK_TIME'] // 1000)

        for bid in c['BIDS']:
            snapshot.bid_prices.append(bid['BID_PRICE'])
            snapshot.bid_sizes.append(bid['TOTAL_VOLUME'])

        for ask in c['ASKS']:
            snapshot.ask_prices.append(ask['ASK_PRICE'])
            snapshot.ask_sizes.append(ask['TOTAL_VOLUME'])

        snapshot_list.append(snapshot)

    return snapshot_list

def on_message(orderbook_run, msg):
    if not msg:
        logging.error('the message is not valid')

    snapshot_list = _msg_to_snapshot_list(msg)
    for snapshot in snapshot_list:
        orderbook_run.on_update(snapshot)


class OrderbookRun():
    def __init__(self, subscription_id = None):
        super().__init__()
        Thread(target=run_loop, args=(self, subscription_id,)).start()

    def on_update(self, snapshot):
        pass
