import json, os
import hashlib
from google.cloud import pubsub_v1
from ingest.streaming.aggregation import BarWithTime, Bar, Trade
from ingest.streaming.aggregations_run import AggregationsRun
from threading import Thread
import util.logging as logging

if_print_message = False

_cnt_msg = 0

def run_loop(aggregations_run, subscription_id):
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_id
    )

    def callback(message_payload):
        msg = json.loads(message_payload.data.decode('utf-8'))
        message_payload.ack()
        on_message(aggregations_run, msg)

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print("Listening for messages on {}\n".format(subscription_path))

    try:
        streaming_pull_future.result()
    except Exception as ex:  # noqa
        logging.error(ex)
        streaming_pull_future.cancel()

def _binance_kline_msg_to_on_bar_with_time(msg):
    keys = ['s', 'o', 'h', 'l', 'c', 'v', 't']
    for key in keys:
        if key not in msg:
            raise Exception('"{key}" field not present in the message: {msg}'.format(key=key, msg=msg))

    symbol = msg['s']

    hashed_v = int(hashlib.sha256(symbol.encode('utf-8')).hexdigest(), 16)
    open_, high, low, close_ = float(msg['o']), float(msg['h']), float(msg['l']), float(msg['c'])
    volume = float(msg['v'])
    timestamp_milli = int(msg['t'])
    timestamp_second = timestamp_milli // 1000

    t = BarWithTime.truncate_to_minute(timestamp_second)
    bar = Bar(symbol, open_, high, low, close_, volume)
    bar_with_time = BarWithTime(t, bar)
    return bar_with_time

def _on_kline_message(aggregations_run, msg):
    global _cnt_msg
    _cnt_msg += 1
    if _cnt_msg % 100 == 0 and if_print_message:
        print("< kline: {msg}".format(msg=msg))

    if 'k' not in msg:
        logging.error('"k" field not present in the kline message: {msg}'.format(msg=msg))
    k = msg['k']
    bar_with_time = _binance_kline_msg_to_on_bar_with_time(k)
    if bar_with_time:
        aggregations_run.on_bar_with_time(bar_with_time)
    else:
        pass # print('does not correspond to this shard')

def _binance_agg_trade_msg_to_trade(msg):
    keys = ['s', 'p', 'q', 'T']
    for key in keys:
        if key not in msg:
            raise Exception('"{key}" field not present in the message: {msg}'.format(key=key, msg=msg))

    symbol = msg['s']
    price = float(msg['p'])
    volume = float(msg['q'])
    timestamp_milli = int(msg['T'])
    timestamp_second = timestamp_milli // 1000
    t = BarWithTime.truncate_to_minute(timestamp_second)
    timestamp_second = int(t.strftime('%s'))
    trade = Trade(timestamp_second, symbol, price, volume)
    return trade

def _binance_trade_msg_to_trade(msg):
    return _binance_agg_trade_msg_to_trade(msg)

def _on_agg_trade_message(aggregations_run, msg):
    global _cnt_msg
    _cnt_msg += 1
    if _cnt_msg % 100 == 0 and if_print_message:
        print("< aggTrade: {msg}".format(msg=msg))

    trade = _binance_agg_trade_msg_to_trade(msg)
    if trade:
        aggregations_run.on_trade(trade)
        pass
    else:
        pass

def _on_trade_message(aggregations_run, msg):
    global _cnt_msg
    _cnt_msg += 1
    if _cnt_msg % 100 == 0 and if_print_message:
        print("< trade: {msg}".format(msg=msg))

    trade = _binance_trade_msg_to_trade(msg)
    if trade:
        aggregations_run.on_trade(trade)
        pass
    else:
        pass

def _on_undefined_message(aggregations_run, msg):
    print("< (undefined) {msg}".format(msg=msg))
    logging.error("< (undefined) {msg}".format(msg=msg))

def on_message(aggregations_run, msg):
    if not msg:
        logging.error('the message is not valid')

    if 'e' not in msg:
        logging.error('"e" field not present in the message: {msg}'.format(msg=msg))
    e = msg['e']
    if e == 'kline':
        _on_kline_message(aggregations_run, msg)
    elif e == 'aggTrade':
        _on_agg_trade_message(aggregations_run, msg)
    elif e == 'trade':
        _on_trade_message(aggregations_run, msg)
    else:
        _on_undefined_message(aggregations_run, msg)

class BinanceAggregationsRun(AggregationsRun):
    def __init__(self, subscription_id = None, a_current_time = None):
        super().__init__(
            a_current_time=a_current_time
        )

        Thread(target=run_loop, args=(self, subscription_id,)).start()
