from strategy.factors.bar_with_times_factors.factor import BarWithTimesFactor
import util.logging
import numpy as np
from enum import Enum
import json, datetime

class SIMPLE_SUDDEN_MOVE_MODE(Enum):
    DROP_SIGNAL = 1
    JUMP_SIGNAL = 2
    NO_SIGNAL = 3

class SimpleSuddenMoveParameter:
    def __init__(self,
                 change_window_minutes,
                 change_threshold
                 ):
        self.change_window_minutes = change_window_minutes
        self.change_threshold = change_threshold


class SimpleSuddenMove(BarWithTimesFactor):
    '''
    This is implemented to privde for cryptocurrency factor service.
    '''

    def __init__(self, symbol, aggregation, param):
        super().__init__(symbol, aggregation)
        self.param = param

    def _get_change(self, change_window_minutes = 10, query_range_minutes = 1):
        '''
        return the change that is used to decide the trading signal.

        :param change_window_minutes: the minutes timestamp difference between current and prev
        :param query_range_minutes: e.g. if this is 10 minutes, it gets the change up down to past 10 minutes from now.
        :return: a value of numpy.float64 type
        '''
        return self.get_change('close', change_window_minutes, query_range_minutes)

    def get(self):
        '''
        Gets if the signal is positive for entering in a position.

        A long / short position is taken when the signal changes into neutral after staying in long/short.
        The intention is to avoid early entry into positions.

        :return:
        '''

        change = self._get_change(change_window_minutes = self.param.change_window_minutes, query_range_minutes = 1)
        change = round(change, 3)
        if np.isnan(change):
            return SIMPLE_SUDDEN_MOVE_MODE.NO_SIGNAL, {}
        change_abs = abs(change)
        if np.isnan(change_abs):
            return SIMPLE_SUDDEN_MOVE_MODE.NO_SIGNAL, {}

        if change < self.param.change_threshold and change > -1 * self.param.change_threshold:
            return SIMPLE_SUDDEN_MOVE_MODE.NO_SIGNAL, {}

        cp = self._get_close_price()
        msg = {
            "symbol": self.symbol,
            "time": str(datetime.datetime.utcfromtimestamp(int(self.get_latest_time().timestamp()))),
            "price": cp,
            "change_window_minutes": self.param.change_window_minutes,
            "change_threshold": self.param.change_threshold,
            "change": change
        }

        if change > self.param.change_threshold:
            util.logging.debug("jump signal for {symbol} is observed. msg: {msg}".format(
                 symbol=self.symbol, msg=json.dumps(msg)))
            return SIMPLE_SUDDEN_MOVE_MODE.JUMP_SIGNAL, msg
        elif change < -1 * self.param.change_threshold:
            util.logging.debug("drop signal for {symbol} is observed. msg: {msg}".format(
                 symbol=self.symbol, msg=json.dumps(msg)))
            return SIMPLE_SUDDEN_MOVE_MODE.DROP_SIGNAL, msg

        return SIMPLE_SUDDEN_MOVE_MODE.NO_SIGNAL, {}
