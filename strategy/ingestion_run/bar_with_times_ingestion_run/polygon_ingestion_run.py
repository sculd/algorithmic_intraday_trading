from strategy.ingestion_run.ingestion_run import IngestionRun
from ingest.streaming.polygon_run import on_message

class PolygonIngestionRun(IngestionRun):
    def __init__(self, strategy_run, subscription_id):
        super().__init__(strategy_run, subscription_id, on_message)


