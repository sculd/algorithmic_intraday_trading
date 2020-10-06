import json, os
import hashlib
from strategy.ingestion_run.ingestion_run import IngestionRun
import util.logging as logging


def on_message(publish_run, msg):
    if not msg:
        logging.error('the message is not valid')
    publish_run.on_message(msg)


class CryptowatchIngestionRun(IngestionRun):
    def __init__(self, publish_run, subscription_id):
        super().__init__(publish_run, subscription_id, on_message)


