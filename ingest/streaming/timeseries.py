import datetime
import pytz


class TimeseriesValue:
    def __init__(self, symbol, value_name, value):
        self.symbol, self.value_name, self.value = symbol, value_name, value

    def get_tuple_names(self):
        return ('symbol', self.value_name, )

    def to_tuple(self):
        return (self.symbol, self.value, )

class TimeseriesValueWithTime:
    def __init__(self, time, timeseries_value):
        '''

        :param time: datetime instance in utc timezone
        :param bar:
        '''
        self.time = time
        self.timeseries_value = timeseries_value

    def get_minute_tuple_names(self):
        return ('datetime',) + self.timeseries_value.get_tuple_names()

    def to_tuple(self):
        return (self.time,) + self.timeseries_value.to_tuple()

class Timeseries:
    def __init__(self, symbol, value_name, timeseries_value_with_time = None):
        self.symbol = symbol
        self.value_name = value_name
        self.timeseries_value_with_time = timeseries_value_with_time if timeseries_value_with_time else []
        self.t_now_tz = None

    def _set_now_tz(self, now_tz):
        '''
        for test only
        :param now_tz: timezone aware current time
        :return:
        '''
        self.t_now_tz = now_tz

    def _get_t_now_tz(self):
        if self.t_now_tz:
            return self.t_now_tz
        t_now = datetime.datetime.utcnow()
        return pytz.utc.localize(t_now)

    def get_change(self, change_window_minutes, query_range_minutes):
        '''
        Gets the (cur_val - prev_cal) / prev_cal.

        :param change_window_minutes: the minutes timestamp difference between current and prev
        :param query_range_minutes: e.g. if this is 10 minutes, it gets the change up down to past 10 minutes from now.
        :return: Aggregation with the time series bars for
        '''
        res = Timeseries(self.symbol, 'close')

        timeseries_value_with_time = []
        t_stop_before = self._get_t_now_tz() - datetime.timedelta(minutes=query_range_minutes)
        i = len(self.timeseries_value_with_time) - 1
        while i >= 0:
            t_i = self.timeseries_value_with_time[i].time
            if t_i < t_stop_before:
                break
            t_look_no_before = t_i - datetime.timedelta(minutes=change_window_minutes)
            j = i
            prev_val = None
            while j >= 0:
                t_j = self.timeseries_value_with_time[j].time
                if t_j < t_look_no_before:
                    break
                prev_val = self.timeseries_value_with_time[j].timeseries_value.value
                j -= 1

            if prev_val is None:
                break

            cur_val = self.timeseries_value_with_time[i].timeseries_value.value
            change_val = (cur_val - prev_val) / prev_val

            ts_v_w_time = TimeseriesValueWithTime(t_i, TimeseriesValue(self.symbol, self.value_name, change_val))
            timeseries_value_with_time.append(ts_v_w_time)
            i -= 1

        res.timeseries_value_with_time = timeseries_value_with_time[::-1]
        return res
