import argparse
import os, datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import util.logging as logging
from strategy.bar_publish.cryptowatch_run import CryptoWatchBarPublishRun


def run(subscription_id):
    dt_str = str(datetime.datetime.now())
    logging.info('starting for {dt_str}'.format(dt_str=dt_str))
    _ = CryptoWatchBarPublishRun(subscription_id)

if __name__ == '__main__':
    logging.set_log_name('cryptowatch_simple_sudden_move_publish')
    parser = argparse.ArgumentParser()
    pubsub_subscription_id_default = os.getenv('CRYPTOWATCH_PUBSUB_BARSPUBLISH_SUBSCRIPTION_ID')
    parser.add_argument("-s", "--subscription_id", default=pubsub_subscription_id_default, help="pubsub subscription id to read the stream from.")
    args = parser.parse_args()

    run(args.subscription_id)
