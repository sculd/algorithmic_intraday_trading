import argparse
import os, datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import util.logging as logging
from strategy.signal_publish.cryptowatch_run import CryptoWatchSignalPublishRun


def run(subscription_id, publish_topic):
    dt_str = str(datetime.datetime.now())
    logging.info('starting for {dt_str}'.format(dt_str=dt_str))
    _ = CryptoWatchSignalPublishRun(subscription_id, publish_topic)

if __name__ == '__main__':
    logging.set_log_name('cryptowatch_simple_sudden_move_publish')
    parser = argparse.ArgumentParser()
    pubsub_subscription_id_default = os.getenv('CRYPTOWATCH_PUBSUB_SUBSCRIPTION_ID')
    pubsub_topic_id_default = os.getenv('CRYPTOWATCH_PUBSUB_TOPIC_ID')
    parser.add_argument("-s", "--subscription_id", default=pubsub_subscription_id_default, help="pubsub subscription id to read the stream from.")
    parser.add_argument("-p", "--publish_topic", default=pubsub_topic_id_default, help="pubsub topic id to publish the signals.")
    args = parser.parse_args()

    run(args.subscription_id, args.publish_topic)
