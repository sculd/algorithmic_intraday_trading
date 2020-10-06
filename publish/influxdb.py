import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

_ORG = "market_signal"
_BUCKET = "market_signal"
_TOKEN = os.getenv('INFLUXDB_TOKEN')

_client = InfluxDBClient(url="https://us-central1-1.gcp.cloud2.influxdata.com", token=_TOKEN, org=_ORG)
_write_api = _client.write_api(write_options=SYNCHRONOUS)


def publish(experiment_name, tag_dict, field_dict):
    p = Point(experiment_name)

    for tag_key, tag_value in tag_dict.items():
        p = p.tag(tag_key, tag_value)

    for field_key, field_value in field_dict.items():
        p = p.field(field_key, float(field_value))

    _write_api.write(bucket=_BUCKET, record=p)

