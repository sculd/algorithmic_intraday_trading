import argparse
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import config
import util.logging as logging
import strategy.profit
from strategy.bar_with_times_strategy.sudden_move.trend_reversal.equity.run_csv import SuddenMoveTrendReversalTradeStrategyCsvRun
from ingest.imports.bq import EXPORT_MODE, DATASET_MODE
import ingest.imports.util

def run_multiple_files(csv_filenames):
    profit_stats = []
    profit_stat = strategy.profit.ProfitStat(None)
    for csv_filename in csv_filenames:
        print('Reading {f}'.format(f=csv_filename))
        csv_run = run(csv_filename)
        profit_stats.append((csv_filename, csv_run.profit_stat))
        profit_stat.union(csv_run.profit_stat)
        print(str(profit_stat))
        profit_stat.print_records()

    print()
    for csv_filename, ps in profit_stats:
        print('csv_filename:', csv_filename)
        print('profit_stat:')
        print(str(ps))
        print()

    print('total stat:')
    print(str(profit_stat))
    profit_stat.print_cumulative_profit()

def run(csv_filename):
    with open(csv_filename) as f:
        sorted_file = sorted(f)

    csv_filename_sorted = csv_filename + '.sorted'
    with open(csv_filename_sorted, 'w') as f:
        f.writelines(sorted_file)

    cfg = config.load('config.us.yaml')
    logging.info('starting for {csv_filename}'.format(csv_filename=csv_filename))
    csv_run = SuddenMoveTrendReversalTradeStrategyCsvRun(config.get_positionsize(cfg), csv_filename_sorted)
    return csv_run

if __name__ == '__main__':
    logging.set_log_name(None)
    parser = argparse.ArgumentParser()
    # 'polygon_hour_bucket_2020-04-06T09:00:00_2020-04-06T10:00:00'
    #parser.add_argument("-c", "--csv_filename", default='data/polygon_example.csv', help="csv file source.")

    #parser.add_argument("-c", "--csv_filename", default='data/2020-06-10/polygon_zhour_bucket_2020-06-10.csv', help="csv file source.")
    #parser.add_argument("-c", "--csv_filename", default='data/stock_minute_ALL_2020-08-03 06:30:00_to_2020-08-03 13:00:00.csv', help="csv file source.")
    parser.add_argument("-c", "--csv_filename", default='data/stock_minute_window60_ALL_2020-09-29 06:30:00_to_2020-09-29 13:00:00.csv', help="csv file source.")
    parser.add_argument("-d", "--dryrun", action="store_true", help="dryrun executes no real buy/sell trades")
    args = parser.parse_args()

    run(args.csv_filename)

    csv_filenames = [
        ingest.imports.util.get_imported_file_name(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE,[], ingest.imports.util.market_open_epoch_seconds('2020', '09', '01'), ingest.imports.util.market_close_epoch_seconds('2020', '09', '01'), 60),
        ingest.imports.util.get_imported_file_name(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE,[], ingest.imports.util.market_open_epoch_seconds('2020', '09', '02'), ingest.imports.util.market_close_epoch_seconds('2020', '09', '02'), 60),
        ingest.imports.util.get_imported_file_name(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE,[], ingest.imports.util.market_open_epoch_seconds('2020', '09', '03'), ingest.imports.util.market_close_epoch_seconds('2020', '09', '03'), 60),
        ingest.imports.util.get_imported_file_name(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.market_open_epoch_seconds('2020', '09', '04'), ingest.imports.util.market_close_epoch_seconds('2020', '09', '04'), 60),
        ingest.imports.util.get_imported_file_name(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.market_open_epoch_seconds('2020', '09', '08'), ingest.imports.util.market_close_epoch_seconds('2020', '09', '08'), 60),
        ingest.imports.util.get_imported_file_name(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.market_open_epoch_seconds('2020', '09', '09'), ingest.imports.util.market_close_epoch_seconds('2020', '09', '09'), 60),
    ]

    #run_multiple_files(csv_filenames)


