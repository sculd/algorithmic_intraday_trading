import os
import market.tdameritrade.common
from tda.client import Client

_ACCOUNT_NUMBER = os.getenv('TD_ACCOUNT_ID')

class Holdings:
    def __init__(self):
        self.client = market.tdameritrade.common.get_client()

    def get(self):
        resp = self.client.get_accounts(fields=[Client.Account.Fields.POSITIONS])
        if not resp or not resp.ok:
            return {}

        return resp.json()

    def get_quantity(self, symbol):
        accounts = self.get()
        account = None
        for ac in accounts:
            if 'securitiesAccount' not in ac:
                continue
            if 'accountId' not in ac['securitiesAccount']:
                continue
            if ac['securitiesAccount']['accountId'] != _ACCOUNT_NUMBER:
                continue
            account = ac['securitiesAccount']
            break

        if not account:
            return 0

        if 'positions' not in account:
            return 0

        position_list = account['positions']
        if position_list == 'null' or not position_list:
            return 0

        position_list = position_list if type(position_list) is list else [position_list]

        res = 0
        for position in position_list:
            instrument = position['instrument']
            if symbol != instrument['symbol']:
                continue
            res = abs(float(position['shortQuantity']))
            res += abs(float(position['longQuantity']))

        return res

    def get_borrowed_quantity(self, symbol):
        return self.get_quantity(symbol)

