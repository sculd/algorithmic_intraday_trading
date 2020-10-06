import json, os
from google.cloud import pubsub_v1
from pytz import timezone
import ingest.streaming.aggregation
from ingest.streaming.aggregations_run import AggregationsRun
from threading import Thread
import util.logging as logging
import util.symbols

if_print_message = False

_cnt_T = 0
_cnt_A = 0
_cnt_MA = 0

def run_loop(polygon_aggregations_run, subscription_id):
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_id
    )

    def callback(message):
        msg_str = json.loads(message.data.decode('utf-8'))
        message.ack()
        print('[run_loop.callback]', message)
        on_message(polygon_aggregations_run, json.loads(msg_str)[0])

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print("Listening for messages on {}\n".format(subscription_path))

    try:
        streaming_pull_future.result()
    except Exception as ex:  # noqa
        logging.error(ex)
        streaming_pull_future.cancel()

def run_mock_loop(polygon_aggregations_run):
    pass

def _on_status_message(polygon_aggregations_run, msg):
    if if_print_message:
        print("< (status) {msg}".format(msg=msg))

def _t_msg_to_trade(msg):
    keys = ['sym', 'p', 's', 't']
    for key in keys:
        if key not in msg:
            print('"{key}" field not present in the message: {msg}'.format(key=key, msg=msg))
    symbol = msg['sym']
    price = msg['p']
    volume = msg['s']
    timestamp_milli = int(msg['t'])
    timestamp_second = timestamp_milli // 1000
    trade = ingest.streaming.aggregation.Trade(timestamp_second, symbol, price, volume)
    return trade

def _a_msg_to_bar_with_time(msg):
    keys = ['sym', 'o', 'h', 'l', 'c', 'v', 's']
    for key in keys:
        if key not in msg:
            raise Exception('"{key}" field not present in the message: {msg}'.format(key=key, msg=msg))

    symbol = msg['sym']
    timestamp_milli = float(msg['s'])
    timestamp_second = timestamp_milli // 1000
    o, h, l, c, v = msg['o'], msg['h'], msg['l'], msg['c'], msg['v']
    o, h, l, c, v = float(o), float(h), float(l), float(c), float(v)
    b = ingest.streaming.aggregation.Bar(symbol, o, h, l, c, v)
    bwt = ingest.streaming.aggregation.BarWithTime(ingest.streaming.aggregation.BarWithTime.epoch_seconds_to_datetime(timestamp_second), b)
    return bwt

def _on_T_message(polygon_aggregations_run, msg):
    global _cnt_T
    print('_on_T_message')
    _cnt_T += 1
    trade = _t_msg_to_trade(msg)
    polygon_aggregations_run.on_trade(trade)

def _on_Q_message(polygon_aggregations_run, msg):
    if if_print_message:
        print("< (Q) {msg}".format(msg=msg))

def _on_A_message(polygon_aggregations_run, msg):
    global _cnt_A
    _cnt_A += 1
    if _cnt_A % 100 == 0 and if_print_message:
        print("< (A) {msg}".format(msg=msg))
    bwt = _a_msg_to_bar_with_time(msg)
    polygon_aggregations_run.on_bar_with_time(bwt)

def _on_AM_message(polygon_aggregations_run, msg):
    global _cnt_AM
    _cnt_AM += 1
    if if_print_message:
        print("< (AM) {msg}".format(msg=msg))

def _on_undefined_message(polygon_aggregations_run, msg):
    if if_print_message:
        print("< (undefined) {msg}".format(msg=msg))
    logging.error("< (undefined) {msg}".format(msg=msg))

def on_message(polygon_aggregations_run, msg):
    if not msg:
        logging.error('the message is not valid')

    if type(msg) is str:
        msg = json.loads(msg)

    if type(msg) is list:
        for m in msg:
            on_message(polygon_aggregations_run, m)
        return

    if 'ev' not in msg:
        logging.error('"ev" field not present in the message: {msg}'.format(msg=msg))
    ev = msg['ev']
    if ev == 'status':
        _on_status_message(polygon_aggregations_run, msg)
    elif ev == 'T':
        _on_T_message(polygon_aggregations_run, msg)
    elif ev == 'Q':
        _on_Q_message(polygon_aggregations_run, msg)
    elif ev == 'A':
        _on_A_message(polygon_aggregations_run, msg)
    elif ev == 'AM':
        _on_AM_message(polygon_aggregations_run, msg)
    else:
        _on_undefined_message(polygon_aggregations_run, msg)

class PolygonAggregationsMockRun(AggregationsRun):
    def __init__(self):
        super(PolygonAggregationsMockRun, self).__init__()
        Thread(target=run_mock_loop, args=(self,)).start()

class PolygonAggregationsRun(AggregationsRun):
    def __init__(self, subscription_id = None):
        super().__init__()
        Thread(target=run_loop, args=(self, subscription_id,)).start()
