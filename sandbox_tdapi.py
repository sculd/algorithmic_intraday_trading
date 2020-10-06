import asyncio, os, json, time

import pprint
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

c = easy_client(
        api_key=_API_KEY,
        redirect_uri=_REDIRECT_URI,
        token_path=_TOKEN_PATH,
        webdriver_func=webdriver.Chrome)



'''
stream_client = StreamClient(c, account_id=_ACCOUNT_ID)

async def read_stream():
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
    await stream_client.nasdaq_book_subs(['GOOG'])

    stream_client.add_nasdaq_book_handler(
            lambda msg: print('[nasdaq_book_handler]', json.dumps(msg, indent=4)))

    stream_client.add_level_one_equity_handler(
            lambda msg: print('[level_one_equity_handler]', json.dumps(msg, indent=4)))

    while True:
        await stream_client.handle_message()

asyncio.get_event_loop().run_until_complete(read_stream())
#'''


import market.tdameritrade.price
import market.tdameritrade.holdings
import market.tdameritrade.long.enter
import market.tdameritrade.long.exit
import market.tdameritrade.short.enter
import market.tdameritrade.short.exit
import market.pick

market_price = market.tdameritrade.price.Price()
holdings = market.tdameritrade.holdings.Holdings()

long_enter = market.tdameritrade.long.enter.get_long(market_price, False)
long_exit = market.tdameritrade.long.exit.get_exit_long(market_price, holdings, False)
short_enter = market.tdameritrade.short.enter.get_short(market_price, False)
short_exit = market.tdameritrade.short.exit.get_exit_short(market_price, holdings, False)

symbol = 'RDFN'

#short_enter.enter(market.pick.EnterPlan(symbol, 50, 10.0))
#time.sleep(5)

print(holdings.get_quantity(symbol))

short_exit.exit(market.pick.ExitPlan(symbol, 10.0))
time.sleep(5)

print(holdings.get_quantity(symbol))




'''
symbol = 'RDFN'
#long_enter.enter(market.pick.EnterPlan(symbol, 50, 40.0))
#time.sleep(5)

print(holdings.get_quantity(symbol))
long_exit.exit(market.pick.ExitPlan(symbol, 40.0))
time.sleep(5)

print(holdings.get_quantity(symbol))
#'''


#'''
r = c.get_accounts(fields=[Client.Account.Fields.POSITIONS])
assert r.ok, r.raise_for_status()
pprint.pprint(r.json())
#'''

