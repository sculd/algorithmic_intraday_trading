import argparse
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import time, datetime
import util.time
import config
import util.logging as logging
from ingest.streaming.export.polygon.hourly_run import HourPolygonAggregationsRun, TIME_UNIT_SECONDS

logging.set_log_name('us_intraday_polygon_hourly_ingest')

def run(dryrun, forcerun):
    logging.info('running hourly ingest')
    trade_run = HourPolygonAggregationsRun(
        subscription_id = os.getenv('FINANCE_STREAM_INTRADAY_INGESTION_PUBSUB_SUBSCRIPTION_ID')
    )

    cfg = config.load('config.us.yaml')
    prev_dump_bucket = int(int(datetime.datetime.now().timestamp()) // TIME_UNIT_SECONDS) * TIME_UNIT_SECONDS
    cnt = 0
    while True:
        cnt += 1
        if cnt % 100 == 0:
            logging.info('start of the loop, utc:', datetime.datetime.utcnow())

        if forcerun:
            time.sleep(2)

        time_bucket = int(int(datetime.datetime.now().timestamp()) // TIME_UNIT_SECONDS) * TIME_UNIT_SECONDS
        if forcerun or (time_bucket != prev_dump_bucket):
            prev_dump_bucket = time_bucket
            #trade_run.to_minute_csv_for_past_hour()
            #trade_run.to_rawdata_csv_for_past_hour()
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
