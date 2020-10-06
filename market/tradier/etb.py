'''
The ETB list contains securities that are able to be sold short with a Tradier Brokerage account. The list is quite comprehensive and can result in a long download response time.
'''

from functools import lru_cache
import time, requests
import market.tradier.common

_URL_PATH_FORMAT_ETB = '/markets/etb'

@lru_cache()
def _get_etb(ttl_hash=None):
    del ttl_hash  # to emphasize we don't use it and to shut pylint up

    print('makring a remote call to get etb')
    response = requests.get(market.tradier.common.URL_BASE_TRADIER + _URL_PATH_FORMAT_ETB,
                            headers=market.tradier.common.get_auth_header_tradier())
    if response.status_code != 200:
        return []

    etb = response.json()
    return set([e['symbol'] for e in etb['securities']['security']])

def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)

def get_etb():
    return _get_etb(ttl_hash=get_ttl_hash(seconds=3600 * 12))
