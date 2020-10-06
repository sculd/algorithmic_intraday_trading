import argparse
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import time, datetime
import util.time
import config
import util.logging as logging
from ingest.streaming.export.orderbook.hourly_run import HourlyOrderbookRun, TIME_UNIT_SECONDS

logging.set_log_name('us_intraday_orderbook_hourly_ingest')

def run(dryrun, forcerun):
    logging.info('running hourly ingest')
    trade_run = HourlyOrderbookRun(
        subscription_id = os.getenv('ORDERBOOK_LEVEL_TWO_STREAM_EXPORT_PUBSUB_SUBSCRIPTION_ID')
    )

    cfg = config.load('config.us.yaml')
    prev_dump_bucket = int(int(datetime.datetime.now().timestamp()) // TIME_UNIT_SECONDS) * TIME_UNIT_SECONDS
    while True:
        logging.info('start of the loop')

        if forcerun:
            time.sleep(2)

        time_bucket = int(int(datetime.datetime.now().timestamp()) // TIME_UNIT_SECONDS) * TIME_UNIT_SECONDS
        if forcerun or (time_bucket != prev_dump_bucket):
            prev_dump_bucket = time_bucket
            trade_run.to_csv_for_past_hour()
        time.sleep(10)

        if forcerun:
            # forcerun runs only once
            print('finishing the forcerun')
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dryrun", action="store_true", help="dryrun executes no real buy/sell trades")
    parser.add_argument("-f", "--forcerun", action="store_true", help="forces run without waiting without observing the schedule.")
    args = parser.parse_args()

    if args.forcerun:
        print('forcerun on')
    run(args.dryrun, args.forcerun)
