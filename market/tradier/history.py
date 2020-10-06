import datetime, json
import config, util.time
import market.tradier.common
import requests
import util.requests

_URL_PATH_FORMAT_QUOTES = '/markets/history'

class MockHistory:
    def __init__(self):
        pass

    def get_price(self, symbol):
        return 50.0

def _two_digit(v):
    return '0' + str(v) if int(v) < 10 else str(v)

class History:
    def __init__(self):
        pass

    def _is_valid_response(self, js):
        if not js:
            return False

        if 'history' not in js or not js['history']:
            return False

        if 'day' not in js['history'] or not js['history']['day']:
            return False

        return True

    def _get_prev_day_prices(self, symbol, days_delta=1):
        cfg = config.load('config.us.yaml')
        d_today = util.time.get_today_tz(cfg)
        d_prevday = d_today - datetime.timedelta(days=days_delta)
        while d_prevday.weekday() >= 5:
            d_prevday -= datetime.timedelta(days=1)

        previous_str = '{year}-{month}-{day}'.format(year=d_prevday.year, month=_two_digit(d_prevday.month), day=_two_digit(d_prevday.day))
        response = util.requests.get_request_session().get(market.tradier.common.URL_BASE_TRADIER + _URL_PATH_FORMAT_QUOTES,
                          params={'symbol': symbol, 'interval': 'daily', 'start': previous_str, 'end': previous_str},
                          headers=market.tradier.common.get_auth_header_tradier()
                          )
        if response.status_code != 200:
            print('the response code for {symbol} hisotry is non-200, {text}'.format(symbol=symbol, text=response.text))
            return {}
        js = response.json()
        if not self._is_valid_response(js):
            # print('the json response for {symbol} history is empty, js: {js}, today: {today}, previous_day: {previous_day}'.format(symbol=symbol, js=js, today=str(datetime.datetime.utcnow()), previous_day=previous_str))
            return {}

        day_list = js['history']['day']
        day_list = day_list if type(day_list) is list else [day_list]

        for day in day_list:
            if day['date'] == previous_str:
                return day
        return {}

    def get_prev_day_close(self, symbol, days_delta=1):
        day = self._get_prev_day_prices(symbol, days_delta=days_delta)
        if not day:
            return 0
        return day['close']

    def get_prev_day_open(self, symbol, days_delta=1):
        day = self._get_prev_day_prices(symbol, days_delta=days_delta)
        if not day:
            return 0
        return day['open'] if 'open' in day else 0

