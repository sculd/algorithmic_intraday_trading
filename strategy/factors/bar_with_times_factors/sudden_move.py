from strategy.factors.bar_with_times_factors.factor import BarWithTimesFactor
import util.logging

import numpy as np
from enum import Enum

class PRICE_MOVE_MODE(Enum):
    DROP_SIGNAL = 1
    JUMP_SIGNAL = 2
    NO_SIGNAL = 3

class SHORT_TERM_PRICE_MOVE_MODE(Enum):
    DROP_SIGNAL = 1
    JUMP_SIGNAL = 2
    NO_SIGNAL = 3

class SuddenMoveParameter:
    def __init__(self,
                 change_threshold_jump,
                 change_threshold_drop,
                 ignore_change_beyond_this_magnitude,
                 price_lower_bound,
                 change_window_minute,
                 change_window_minute_short
                 ):
        self.change_threshold_jump = change_threshold_jump
        self.change_threshold_drop = change_threshold_drop
        self.ignore_change_beyond_this_magnitude = ignore_change_beyond_this_magnitude
        self.price_lower_bound = price_lower_bound
        self.change_window_minute = change_window_minute
        self.change_window_minute_short = change_window_minute_short


class SuddenMove(BarWithTimesFactor):
    def __init__(self, symbol, aggregation, param):
        super().__init__(symbol, aggregation)
        self.param = param
        self.aggregation.set_bar_with_times_max_length(self.param.change_window_minute)

    def get(self):
        sig = self.get_market_signal()
        short_term_sig = self.get_short_term_market_signal(sig)
        return (sig, short_term_sig, )

    def _get_change(self, change_window_minutes = 10, query_range_minutes = 1):
        '''
        return the change that is used to decide the trading signal.

        :param change_window_minutes: the minutes timestamp difference between current and prev
        :param query_range_minutes: e.g. if this is 10 minutes, it gets the change up down to past 10 minutes from now.
        :return: a value of numpy.float64 type
        '''
        return self.get_max_amplitude_change('close', change_window_minutes)

    def get_market_signal(self):
        '''
        Gets if the signal is positive for entering in a position.

        A long / short position is taken when the signal changes into neutral after staying in long/short.
        The intention is to avoid early entry into positions.

        :return:
        '''

        change_window_minutes = self.param.change_window_minute
        change = self._get_change(change_window_minutes = change_window_minutes, query_range_minutes = 1)
        change = round(change, 3)
        #print('{symbol}: long term change: {change}, at {t}'.format(symbol=self.symbol, change=change, t=self.get_latest_time()))
        if np.isnan(change):
            return PRICE_MOVE_MODE.NO_SIGNAL
        change_abs = abs(change)
        if np.isnan(change_abs):
            return PRICE_MOVE_MODE.NO_SIGNAL
        if change_abs > self.param.ignore_change_beyond_this_magnitude:
            cp = self._get_close_price()
            util.logging.warning("for {symbol} long term move was observed but it is of too large size. price: {price}, change: {change} at {t}".format(
                symbol=self.symbol, price=cp, change=change, t=self.get_latest_time()))
            return PRICE_MOVE_MODE.NO_SIGNAL

        abs_min_threshold = min(self.param.change_threshold_jump, abs(self.param.change_threshold_drop))
        if change_abs < abs_min_threshold:
            return PRICE_MOVE_MODE.NO_SIGNAL

        cp = self._get_close_price()
        quantity_minutes = 10
        min_quantity_minutes = self.aggregation.get_minimal_quantity(quantity_minutes, drop_last=True)
        avg_quantity_minutes = self.aggregation.get_avg_quantity(quantity_minutes)
        closes = self._get_value_list('close', change_window_minutes)
        closes_head_str = ','.join(map(lambda v: str(v), closes[:10]))
        closes_tail_str = ','.join(map(lambda v: str(v), closes[-10:]))

        if cp < self.param.price_lower_bound:
            util.logging.debug("for {symbol} long term move was observed but price is too low. price: {price}, change: {change}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                symbol=self.symbol, price=cp, change=change, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.get_latest_time()))
            return PRICE_MOVE_MODE.NO_SIGNAL
        elif change > self.param.change_threshold_jump:
            util.logging.debug("long term jump signal for {symbol} is observed. price: {price}, prices: {pricesh} ... {pricest}, change: {change} at {t}".format(
                 symbol=self.symbol, price=cp, pricesh=closes_head_str, pricest=closes_tail_str, change=change, t=self.get_latest_time()))
            return PRICE_MOVE_MODE.JUMP_SIGNAL
        elif change < self.param.change_threshold_drop:
            util.logging.debug("long term drop signal for {symbol} is observed. price: {price}, prices: {pricesh} ... {pricest}, change: {change} at {t}".format(
                 symbol=self.symbol, price=cp, pricesh=closes_head_str, pricest=closes_tail_str, change=change, t=self.get_latest_time()))
            return PRICE_MOVE_MODE.DROP_SIGNAL

        return PRICE_MOVE_MODE.NO_SIGNAL

    def get_short_term_market_signal(self, long_term_market_signal):
        '''
        Gets if the short term signal is positive for entering in a position.

        A long / short position is taken when the signal changes into neutral after staying in long/short.
        The intention is to avoid early entry into positions.

        :return:
        '''

        change_window_minutes = self.param.change_window_minute_short
        change = self._get_change(change_window_minutes = change_window_minutes, query_range_minutes = 1)
        change = round(change, 3)
        #print('{symbol}: short term change: {change} at {t}'.format(symbol=self.symbol, change=change, t=self.get_latest_time()))
        if long_term_market_signal is not PRICE_MOVE_MODE.NO_SIGNAL:
            util.logging.info('{symbol}: (get_short_term_market_signal) change: {change}'.format(symbol=self.symbol, change=change))

        if np.isnan(change):
            return SHORT_TERM_PRICE_MOVE_MODE.NO_SIGNAL
        change_abs = abs(change)
        if np.isnan(change_abs):
            return SHORT_TERM_PRICE_MOVE_MODE.NO_SIGNAL
        if change_abs > self.param.ignore_change_beyond_this_magnitude:
            cp = self._get_close_price()
            util.logging.warning("for {symbol} short term move was observed but it is of too large size. price: {price}, change: {change} at {t}".format(
                symbol=self.symbol, price=cp, change=change, t=self.get_latest_time()))
            return SHORT_TERM_PRICE_MOVE_MODE.NO_SIGNAL

        abs_min_threshold = min(self.param.change_threshold_jump, abs(self.param.change_threshold_drop)) / 2.0
        if change_abs < abs_min_threshold:
            return SHORT_TERM_PRICE_MOVE_MODE.NO_SIGNAL

        cp = self._get_close_price()

        if change > self.param.change_threshold_jump / 2.0:
            util.logging.debug("short term jump signal for {symbol} is observed. price: {price}, prices: {prices}, change: {change} at {t}".format(
                 symbol=self.symbol, price=cp, prices=self.get_close_list_str(change_window_minutes), change=change, t=self.get_latest_time()))
            return SHORT_TERM_PRICE_MOVE_MODE.JUMP_SIGNAL
        elif change < self.param.change_threshold_drop / 2.0:
            util.logging.debug("short term drop signal for {symbol} is observed. price: {price}, prices: {prices}, change: {change} at {t}".format(
                 symbol=self.symbol, price=cp, prices=self.get_close_list_str(change_window_minutes), change=change, t=self.get_latest_time()))
            return SHORT_TERM_PRICE_MOVE_MODE.DROP_SIGNAL

        return SHORT_TERM_PRICE_MOVE_MODE.NO_SIGNAL
