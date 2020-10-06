import os
from binance.client import Client

_API_KEY = os.getenv('API_KEY_BINANCE')
_API_SECRET = os.getenv('API_SECRET_BINANCE')

_client = None

def get_client():
    global _client
    if _client is not None:
        return _client
    _client = Client(_API_KEY, _API_SECRET)
    return _client

def get_lot_sizes():
    exinfo = get_client().get_exchange_info()
    res = {}
    for symbol_info in exinfo['symbols']:
        if 'USDT' not in symbol_info['symbol']:
            continue
        filters = symbol_info['filters']
        for filter in filters:
            if filter['filterType'] == 'LOT_SIZE':
                res[symbol_info['symbol']] = float(filter['stepSize'])
                break
    return res



