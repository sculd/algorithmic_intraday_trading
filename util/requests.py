import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_request_session = requests.Session()
_retries = Retry(total=5, backoff_factor=0.5)

_request_session.mount('http://', HTTPAdapter(max_retries=_retries))
_request_session.mount('https://', HTTPAdapter(max_retries=_retries))


def get_request_session():
    return _request_session
