import requests
import market.tradier.common

_URL_PATH_FORMAT_ACCOUNT_POSITIONS = '/accounts/{account_id}/positions'


class Holdings:
    def __init__(self):
        pass

    def get(self):
        account_number = market.tradier.common.get_account_account_number()
        response = requests.get(market.tradier.common.URL_BASE_TRADIER + _URL_PATH_FORMAT_ACCOUNT_POSITIONS.format(account_id=account_number),
                          data={},
                          headers=market.tradier.common.get_auth_header_tradier()
                          )
        if response.status_code != 200:
            return {}
        return response.json()

    def get_quantity(self, symbol):
        holdings = self.get()
        position_list = holdings['positions']
        if position_list == 'null':
            return 0
        position_list = position_list if type(position_list) is list else [position_list]

        res = 0
        for position in position_list:
            symbol_position = position['symbol']
            if symbol != symbol_position:
                continue
            res = abs(float(position['quantity']))

        return res

    def get_borrowed_quantity(self, symbol):
        return self.get_quantity(symbol)

