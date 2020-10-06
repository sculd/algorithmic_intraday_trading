import market.ally.allypy as ally

_client = None

def get_client():
    global _client
    if _client is not None:
        return _client
    _client = ally.Ally()
    return _client
