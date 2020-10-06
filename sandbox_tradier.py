import os, requests
import pprint


ACCOUNT_ID = ''

_ACCESS_TOKEN_TRADIER = os.environ['TRADIER_ACCESS_TOKEN']

URL_BASE_TRADIER = 'https://api.tradier.com/v1'
_URL_PATH_USER_PROFILE = '/user/profile'
_URL_PATH_FORMAT_ACCOUNT_BALANCES = '/accounts/{account_id}/balances'
_URL_PATH_FORMAT_ACCOUNT_POSITIONS = '/accounts/{account_id}/positions'
_URL_PATH_FORMAT_ETB = '/markets/etb'

'''
def _get_auth_header_tradier():
    return {
        "Authorization":"Bearer " + _ACCESS_TOKEN_TRADIER,
        'Accept': 'application/json'
    }

def get_account_account_number():
    js = response = requests.get(URL_BASE_TRADIER + _URL_PATH_USER_PROFILE,
            data={},
            headers=_get_auth_header_tradier()
        ).json()

    pprint.pprint(js)
    return js['profile']['account']['account_number']

#'''

'''
account_number = get_account_account_number()
print('account_number:', account_number)

js = requests.get(URL_BASE_TRADIER + _URL_PATH_FORMAT_ACCOUNT_BALANCES.format(account_id=account_number),
                             data={},
                             headers=_get_auth_header_tradier()
                             ).json()

#pprint.pprint(js)


js = requests.get(URL_BASE_TRADIER + _URL_PATH_FORMAT_ACCOUNT_POSITIONS.format(account_id=account_number),
                             data={},
                             headers=_get_auth_header_tradier()
                             ).json()

pprint.pprint(js)
#'''



import market.tradier.history

h = market.tradier.history.History()
print(h.get_prev_day_open('EQ'))



'''
example:

/Users/hjunlim/venvs/datascience/bin/python /Users/hjunlim/projects/us_intraday_trading/sandbox_tradier.py
{'profile': {'account': {'account_number': '6YA13537',
                         'classification': 'individual',
                         'date_created': '2020-05-28T12:21:28.000Z',
                         'day_trader': False,
                         'last_update_date': '2020-05-28T12:24:04.000Z',
                         'option_level': 0,
                         'status': 'active',
                         'type': 'margin'},
             'id': 'id-9zg0uxenfk',
             'name': 'Hyungjun Lim'}}
account_number: 6YA13537
{'positions': {'position': [{'cost_basis': 49.32,
                             'date_acquired': '2020-06-05T19:16:43.167Z',
                             'id': 1293079,
                             'quantity': 1.0,
                             'symbol': 'KO'},
                            {'cost_basis': -201.33,
                             'date_acquired': '2020-06-09T14:52:12.670Z',
                             'id': 1297662,
                             'quantity': -1.0,
                             'symbol': 'V'}]}}

Process finished with exit code 0

'''

#'''


'''
import market.tradier.etb
etb = market.tradier.etb.get_etb()
print(etb)

etb = market.tradier.etb.get_etb()
print(etb)
#'''


'''
import market.tradier.price

price = market.tradier.price.Price()

print(price.get_price('GOOG'))


import market.tradier.holdings

holdings = market.tradier.holdings.Holdings()

print(holdings.get_quantity('AMZN'))


import market.tradier.long.enter, market.tradier.long.exit
import market.pick
long_enter_plan = market.pick.EnterPlan('KO', 110, 46)

long = market.tradier.long.enter.get_long(price, False)
long.enter(long_enter_plan)

import market.tradier.short.enter, market.tradier.short.exit
short_enter_plan = market.pick.EnterPlan('KO', 110, 46)

short = market.tradier.short.enter.get_short(price, False)
short.enter(short_enter_plan)
#'''



