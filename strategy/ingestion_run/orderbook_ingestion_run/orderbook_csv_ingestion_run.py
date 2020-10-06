import json, os, time
from ingest.streaming.orderbook import OrderbookSnapshot
from pytz import timezone

def run_loop(strategy_run, csv_filename, on_orderbook_snapshot):
    def line_to_orderbook_snapshot(line):
        '''
        epoch_seconds,symbol,bid_price_0,bid_price_1,bid_price_2,bid_volume_0,bid_volume_1,bid_volume_2,ask_price_0,ask_price_1,ask_price_2,ask_volume_0,ask_volume_1,ask_volume_2
        1592580183,TSLA,1006.54,1006.4,1006.25,120,100,100,1006.77,1006.88,1006.9,90,700,200

        :param line:
        :return:
        '''
        epoch_seconds, symbol, bid_price_0, bid_price_1, bid_price_2, bid_volume_0, bid_volume_1, bid_volume_2, ask_price_0, ask_price_1, ask_price_2, ask_volume_0, ask_volume_1, ask_volume_2 = line.strip().split(',')
        if epoch_seconds == 'epoch_seconds': return None
        o = OrderbookSnapshot(symbol)
        o.epoch_seconds = int(epoch_seconds)
        o.bid_prices = [float(bid_price_0), float(bid_price_1), float(bid_price_2)]
        o.bid_sizes = [float(bid_volume_0), float(bid_volume_1), float(bid_volume_2)]
        o.ask_prices = [float(ask_price_0), float(ask_price_1), float(ask_price_2)]
        o.ask_sizes = [float(ask_volume_0), float(ask_volume_1), float(ask_volume_2)]
        return o

    for line in open(csv_filename):
        bar_with_time = line_to_orderbook_snapshot(line)
        if not bar_with_time: continue
        on_orderbook_snapshot(strategy_run, bar_with_time)

    strategy_run.on_ingestion_end()

def on_orderbook_snapshot(strategy_run, orderbook_snapshot):
    strategy_run.on_orderbook_snapshot(orderbook_snapshot)

class OrerbookCsvIngestionRun():
    def __init__(self, strategy_run, csv_filename):
        run_loop(strategy_run, csv_filename, on_orderbook_snapshot)
