import json, os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
from google.cloud import pubsub_v1
from threading import Thread
import util.logging as logging


def run_loop(strategy_run, subscription_id, on_message):
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    project_id = 'trading-290017'

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_id
    )

    def callback(message_payload):
        msg = json.loads(message_payload.data.decode('utf-8'))
        message_payload.ack()
        on_message(strategy_run, msg)

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print("Listening for messages on {}\n".format(subscription_path))

    try:
        streaming_pull_future.result()
    except Exception as ex:  # noqa
        logging.error(ex)
        streaming_pull_future.cancel()

def on_message(strategy_run, msg):
    print(msg)

#Thread(target=run_loop, args=(None, os.getenv('BINANCE_STREAM_INTRADAY_TRADING_PUBSUB_SUBSCRIPTION_ID'), on_message)).start()
Thread(target=run_loop, args=(None, 'binance_stream_intraday_trading', on_message)).start()

print('done')





