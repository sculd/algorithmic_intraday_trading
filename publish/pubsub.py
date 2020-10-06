import os, json
from google.cloud import pubsub_v1

_project_id = os.getenv('GOOGLE_CLOUD_PROJECT'),

_publisher = None
def _get_publisher():
    global _publisher
    if _publisher is None:
        _publisher = pubsub_v1.PublisherClient()
    return _publisher

def publish(topic, msg_dict):
    def _get_full_topic_name():
        return 'projects/{project_id}/topics/{topic}'.format(
            project_id=_project_id,
            topic=topic,
        )

    publisher = _get_publisher()
    publisher.publish(_get_full_topic_name(), json.dumps(msg_dict).encode())
