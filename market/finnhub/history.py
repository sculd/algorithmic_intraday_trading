import datetime, time
import config, util.time
import market.finnhub.common

_RESOLUTION_MINUTE = '1'

def _two_digit(v):
    return '0' + str(v) if int(v) < 10 else str(v)

class History:
    def __init__(self):
        self.cfg = config.load('config.us.yaml')

    def _is_valid_response(self, js):
        if not js:
            return False

        if 'history' not in js or not js['history']:
            return False

        if 'day' not in js['history'] or not js['history']['day']:
            return False

        return True

    def _get_prev_day_datetime(self, days_delta):
        d_today = util.time.get_today_tz(self.cfg)
        d_prevday = d_today - datetime.timedelta(days=days_delta)
        while d_prevday.weekday() >= 5:
            d_prevday -= datetime.timedelta(days=1)
        return d_prevday

    def _get_market_start_datetime(self, days_delta):
        prev_t = self._get_prev_day_datetime(days_delta)
        t = datetime.datetime.strptime('{year}-{month}-{day}T'.format(year=prev_t.year, month=_two_digit(prev_t.month), day=_two_digit(prev_t.day)) + self.cfg['market']['open'], '%Y-%m-%dT%H:%M:%S')
        tz = config.get_tz(self.cfg)
        return tz.localize(t)

    def get_prev_day_intraday_close(self, symbol, days_delta=1, minutes_delta=1):
        '''

        :param symbol:
        :param days_delta: how many days ago from today?
        :param minutes_delta:  how many minutes after the market open (9.30am ET)
        :return:
        '''
        t_martket_start = self._get_market_start_datetime(days_delta)

        from_epoch_seconds = int((t_martket_start + datetime.timedelta(minutes=minutes_delta)).timestamp())
        to_epoch_seconds = from_epoch_seconds + 60
        retries = 0
        while True:
            try:
                candles = market.finnhub.common.get_client().stock_candles(symbol, _RESOLUTION_MINUTE, from_epoch_seconds, to_epoch_seconds)
                break
            except Exception as e:
                print(e)
                retries += 1
                print('retries', retries, symbol, 'days_delta', days_delta, 'minutes_delta', minutes_delta)
                if retries <= 4:
                    time.sleep(retries)
                    continue
                return 0

        if not candles:
            return 0
        if not candles.c:
            return 0

        return candles.c[0]


    def get_prev_day_intraday_early_closes(self, symbol, days_delta=1):
        '''

        :param symbol:
        :param days_delta: how many days ago from today?
        :param minutes_delta:  how many minutes after the market open (9.30am ET)
        :return:
        '''
        t_martket_start = self._get_market_start_datetime(days_delta)

        from_epoch_seconds = int((t_martket_start + datetime.timedelta(minutes=0)).timestamp())
        to_epoch_seconds = from_epoch_seconds + 60 * 30
        retries = 0
        while True:
            try:
                candles = market.finnhub.common.get_client().stock_candles(symbol, _RESOLUTION_MINUTE, from_epoch_seconds, to_epoch_seconds)
                break
            except Exception as e:
                print(e)
                retries += 1
                print('retries', retries, symbol, 'days_delta', days_delta)
                if retries <= 4:
                    time.sleep(retries)
                    continue
                return 0

        if not candles:
            return 0, 0, 0
        if not candles.c:
            return 0, 0, 0

        if len(candles.c) < 10:
            print('the response does not have the full history', len(candles.c), candles)
        return candles.c[0], candles.c[len(candles.c) // 2], candles.c[-1]
