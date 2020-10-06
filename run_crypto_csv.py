import argparse
import os, datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import config_binance
import util.logging as logging
from strategy.bar_with_times_strategy.box_range.exit_momentum.crypto.run_rawdata_csv import BoxRangeExitMomentumTradeStrategyCsvRun


def run(csv_filename):
    cfg = config_binance.load('config.binance.yaml')
    dt_str = str(datetime.datetime.now())
    logging.info('starting for {dt_str}'.format(dt_str=dt_str))
    _ = BoxRangeExitMomentumTradeStrategyCsvRun(config_binance.get_positionsize(cfg), csv_filename)

if __name__ == '__main__':
    logging.set_log_name(None)
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv_filename", default='data/2020-07-12/binance_rawdata_bucket_2020-07-12.csv', help="csv file source.")
    parser.add_argument("-d", "--dryrun", action="store_true", help="dryrun executes no real buy/sell trades")
    args = parser.parse_args()

    with open(args.csv_filename) as f:
        sorted_file = sorted(f)

    with open(args.csv_filename + '.sorted', 'w') as f:
        f.writelines(sorted_file)

    run(args.csv_filename + '.sorted')
