from ingest.streaming.aggregation import BarWithTime, Bar, Trade
import datetime

def run_loop(strategy_run, csv_filename, on_trade):
    def line_to_agg_trade_msg_to_trade(line):
        '''
        datetime,symbol,open,high,low,close,volume
        1586160000,PLAY,10.2,10.2,10.2,10.2,0

        :param line:
        :return:
        '''
        timestamp_seconds, symbol, price, volume = line.strip().split(',')
        if timestamp_seconds == 'timestamp_seconds': return None
        # timestamp_seconds,symbol,price,volume
        try:
            timestamp_seconds_v, price_v, volume_v = int(timestamp_seconds), float(price), float(volume)
        except ValueError as ex:
            timestamp_seconds_v, price_v, volume_v = int(datetime.datetime.fromisoformat(timestamp_seconds).timestamp()), float(price), float(volume)
        trade = Trade(timestamp_seconds_v, symbol, price_v, volume_v)
        return trade

    for line in open(csv_filename):
        trade = line_to_agg_trade_msg_to_trade(line)
        if not trade: continue
        on_trade(strategy_run, trade)

    strategy_run.on_ingestion_end()

def on_trade(strategy_run, trade):
    strategy_run.on_trade(trade)

class BarWithTimesCsvIngestionRun():
    def __init__(self, strategy_run, csv_filename):
        run_loop(strategy_run, csv_filename, on_trade)
