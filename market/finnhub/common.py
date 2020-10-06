import finnhub, os

# Configure API key
_configuration = finnhub.Configuration(
    api_key={
        'token': os.getenv('FINNHUB_API_KEY')
    }
)

_finnhub_client = None

def get_client():
    global _finnhub_client
    if _finnhub_client is None:
        _finnhub_client = finnhub.DefaultApi(finnhub.ApiClient(_configuration))

    return _finnhub_client


