from ingest.streaming.aggregation import Aggregation
from strategy.factors.factor import Factor


class BarWithTimesFactor(Factor):
    def __init__(self, symbol, aggregation):
        super().__init__(symbol)
        self.aggregation = aggregation

    def _get_value_list(self, column_name, query_range_minutes):
        v_list = self.aggregation._get_value_lists([column_name], 1 + query_range_minutes, drop_last=False)[column_name]
        return v_list

    def get_change_list(self, column_name, change_window_minutes, query_range_minutes):
        '''
        Gets the (cur_val - prev_cal) / prev_cal.

        :param change_window_minutes: the minutes timestamp difference between current and prev
        :param query_range_minutes: e.g. if this is 10 minutes, it gets the change up down to past 10 minutes from now.
        :return:
        '''
        v_list = self.aggregation._get_value_lists([column_name], change_window_minutes + query_range_minutes, drop_last=False)[column_name]
        l = len(v_list)
        if l == 0:
            return []
        res = []
        first_val = v_list[0]
        for i in range(l):
            nom_v = 0 if i < change_window_minutes else v_list[i] - v_list[i - change_window_minutes]
            denom_v = first_val if i < change_window_minutes else v_list[i - change_window_minutes]
            res.append(1.0 * nom_v / denom_v)
        return res[-query_range_minutes:]

    def get_change(self, column_name, change_window_minutes, query_range_minutes):
        '''
        Gets the (cur_val - prev_cal) / prev_cal.

        :param change_window_minutes: the minutes timestamp difference between current and prev
        :param query_range_minutes: e.g. if this is 10 minutes, it gets the change up down to past 10 minutes from now.
        :return:
        '''
        change_list = self.get_change_list(column_name, change_window_minutes, query_range_minutes)
        if len(change_list) == 0:
            return 0
        return change_list[-1]

    def get_max_amplitude_change(self, column_name, change_window_minutes):
        '''
        Gets the change of the maximum size within the window.

        :param change_window_minutes: the minutes timestamp difference between current and prev
        :return:
        '''
        v_list = self.aggregation._get_value_lists([column_name], change_window_minutes + 1, drop_last=False)[column_name]
        l = len(v_list)
        if l == 0:
            return 0
        res = 0
        last_val = v_list[-1]
        for i in range(l-1):
            nom_v = last_val - v_list[i]
            denom_v = v_list[i]
            if denom_v == 0: continue
            change = 1.0 * nom_v / denom_v
            if abs(change) > abs(res):
                res = change

        return res

    def get_close_list_str(self, query_range_minutes):
        '''
        for debugging
        :param column_name:
        :param query_range_minutes:
        :return:
        '''
        return ','.join(map(lambda v: str(v), self._get_value_list('close', query_range_minutes)))

    def _get_close_price(self):
        return self.aggregation._get_close_price()

    def get_latest_time(self):
        return self.aggregation.get_latest_time()

    def get(self):
        pass
