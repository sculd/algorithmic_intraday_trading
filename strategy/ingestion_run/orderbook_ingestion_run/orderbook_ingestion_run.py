import json, os
from strategy.ingestion_run.ingestion_run import IngestionRun
from pytz import timezone
import util.logging as logging
from ingest.streaming.orderbook import OrderbookSnapshot

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
        orderbook_run.on_orderbook_snapshot(snapshot)


class OrderbookIngestionRun(IngestionRun):
    def __init__(self, strategy_run, subscription_id):
        super().__init__(strategy_run, subscription_id, on_message)


