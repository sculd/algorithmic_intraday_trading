import json, os
from google.cloud import pubsub_v1
from threading import Thread
import util.logging as logging


def run_loop(strategy_run, subscription_id, on_message):
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

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

class IngestionRun():
    def __init__(self, strategy_run, subscription_id, on_message):
        Thread(target=run_loop, args=(strategy_run, subscription_id, on_message)).start()
