import os, requests

_ACCESS_TOKEN_TRADIER = os.environ['TRADIER_ACCESS_TOKEN']

URL_BASE_TRADIER = 'https://api.tradier.com/v1'
_URL_PATH_USER_PROFILE = '/user/profile'

def get_auth_header_tradier():
    return {
        "Authorization":"Bearer " + _ACCESS_TOKEN_TRADIER,
        'Accept': 'application/json'
    }

def get_account_account_number():
    js = requests.get(URL_BASE_TRADIER + _URL_PATH_USER_PROFILE,
            data={},
            headers=get_auth_header_tradier()
        ).json()

    return js['profile']['account']['account_number']
