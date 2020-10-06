import os, json

from tda import auth, client
from tda.auth import easy_client
from tda.client import Client
from tda.streaming import StreamClient
from selenium import webdriver
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

_TOKEN_PATH = 'token.pickle'
_API_KEY = os.getenv('TD_API_KEY')
_ACCOUNT_ID = int(os.getenv('TD_ACCOUNT_ID'))
_REDIRECT_URI = 'https://localhost'

_client = None

def get_client():
    global _client
    if _client is None:
        _client = easy_client(
            api_key=_API_KEY,
            redirect_uri=_REDIRECT_URI,
            token_path=_TOKEN_PATH,
            webdriver_func=webdriver.Chrome)

    return _client
