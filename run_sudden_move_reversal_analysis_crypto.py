import argparse
import os, datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import config_binance
import util.logging as logging
import util.current_time
from strategy.bar_with_times_strategy.timeseries_analysis.trend_reserval.crypto.run import SuddenMoveTrendReversalTradeStrategyRun

def run(dryrun, subscription_id):
    logging.set_log_name('crypto_trading')
    cfg = config_binance.load('config.binance.yaml')
    dt_str = str(datetime.datetime.now())
    logging.info('starting for {dt_str}'.format(dt_str=dt_str))
    _ = SuddenMoveTrendReversalTradeStrategyRun(dryrun, config_binance.get_positionsize(cfg), subscription_id = subscription_id, a_current_time=util.current_time.CurrentTime())

if __name__ == '__main__':
    logging.set_log_name('crypto_trading')
    parser = argparse.ArgumentParser()
    pubsub_id_default = os.getenv('BINANCE_STREAM_INTRADAY_TRADING_PUBSUB_SUBSCRIPTION_ID')
    parser.add_argument("-s", "--subscription_id", default=pubsub_id_default, help="pubsub subscription id to read the stream from.")
    parser.add_argument("-d", "--dryrun", action="store_true", help="dryrun executes no real buy/sell trades")
    args = parser.parse_args()

    run(args.dryrun, args.subscription_id)
