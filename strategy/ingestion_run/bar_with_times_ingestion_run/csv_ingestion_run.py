from ingest.streaming.aggregation import BarWithTime, Bar, Trade
import datetime

def run_loop(strategy_run, csv_filename, on_bar_with_time):
    def line_to_agg_trade_msg_to_trade(line):
        '''
        datetime,symbol,open,high,low,close,volume
        1586160000,PLAY,10.2,10.2,10.2,10.2,0

        :param line:
        :return:
        '''
        timestamp, symbol, open_, high, low, close_, volume = line.strip().split(',')
        if timestamp == 'datetime': return None
        try:
            timestamp_v, open_v, high_v, low_v, close_v, volume_v = int(timestamp), float(open_), float(high), float(low), float(close_), float(volume)
        except ValueError as ex:
            timestamp_v, open_v, high_v, low_v, close_v, volume_v = int(datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S%z').timestamp()), float(open_), float(high), float(low), float(close_), float(volume)

        t = BarWithTime.epoch_seconds_to_datetime(timestamp_v)
        bar = Bar(symbol, open_v, high_v, low_v, close_v, volume_v)
        bar_with_time = BarWithTime(t, bar)
        return bar_with_time

    for line in open(csv_filename):
        bar_with_time = line_to_agg_trade_msg_to_trade(line)
        if not bar_with_time: continue
        on_bar_with_time(strategy_run, bar_with_time)

    strategy_run.on_ingestion_end()

def on_bar_with_time(strategy_run, bar_with_time):
    strategy_run.on_bar_with_time(bar_with_time)

class BarWithTimesCsvIngestionRun():
    def __init__(self, strategy_run, csv_filename):
        run_loop(strategy_run, csv_filename, on_bar_with_time)
