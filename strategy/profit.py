import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import datetime
from enum import Enum
import gnuplotlib as gp

class PROFIT_POSITION(Enum):
    LONG = 1
    SHORT= 2

def _position_str(profit_position):
    if profit_position is PROFIT_POSITION.LONG:
        return 'Long'
    elif profit_position is PROFIT_POSITION.SHORT:
        return 'Short'

class PriceSnapshot:
    def __init__(self, price, local_max_price, local_min_price, epoch_seconds, min_quantity, avg_quantity):
        self.price = price
        self.local_max_price = local_max_price
        self.local_min_price = local_min_price
        self.epoch_seconds = epoch_seconds
        self.min_quantity = round(min_quantity, 1)
        self.avg_quantity = round(avg_quantity, 1)

    def __str__(self):
        return 'price: {p}, at: {t}, min quantity: {mq}, avg quantity: {aq}'.format(p=self.price, t=datetime.datetime.utcfromtimestamp(self.epoch_seconds).strftime('%Y-%m-%dT%H:%M:%S'), mq=self.min_quantity, aq=self.avg_quantity)

def get_profit_long(price_snapshot_enter, price_snapshot_exit, round_digit=6):
    entered = price_snapshot_enter.price
    return 0 if entered == 0 else round(1.0 * (price_snapshot_exit.price - entered) / entered, round_digit)

def get_profit_short(price_snapshot_enter, price_snapshot_exit, round_digit=6):
    entered = price_snapshot_enter.price
    return 0 if entered == 0 else round(1.0 * (entered - price_snapshot_exit.price) / entered, round_digit)

def get_profit(price_snapshot_enter, price_snapshot_exit, profit_position):
    if profit_position is PROFIT_POSITION.LONG:
        return get_profit_long(price_snapshot_enter, price_snapshot_exit)
    elif profit_position is PROFIT_POSITION.SHORT:
        return get_profit_short(price_snapshot_enter, price_snapshot_exit)

class ProfitRecord:
    def __init__(self, symbol, profit_position, price_snapshot_enter, price_snapshot_exit):
        self.symbol = symbol
        self.profit_position = profit_position
        self.profit = get_profit(price_snapshot_enter, price_snapshot_exit, profit_position)
        self.price_snapshot_enter = price_snapshot_enter
        self.price_snapshot_exit = price_snapshot_exit

    def __str__(self):
        return 'symbol: {s}, position: {pn}, profit: {pft}%, enter: ({enter}), exit: ({exit})'.format(
            s = self.symbol,
            pn = _position_str(self.profit_position),
            pft = round(self.profit * 100, 3),
            enter = str(self.price_snapshot_enter),
            exit = str(self.price_snapshot_exit)
        )

class ProfitStat:
    def __init__(self, records_capacity):
        self.profit_records = []
        self.records_capacity = records_capacity

    def append(self, profit_record):
        self.profit_records.append(profit_record)
        if self.records_capacity and len(self.profit_records) > self.records_capacity:
            self.profit_records = self.profit_records[-self.records_capacity:]

    def union(self, profit_stat):
        self.profit_records += profit_stat.profit_records

    def clear(self):
        self.profit_records = []

    def _get_total_profit(self, profit_records):
        return round(float(np.sum([p.profit for p in profit_records])), 3) if profit_records else 0

    def _get_min_profit(self, profit_records):
        return round(float(np.min([p.profit for p in profit_records])), 3) if profit_records else 0

    def _get_max_profit(self, profit_records):
        return round(float(np.max([p.profit for p in profit_records])), 3) if profit_records else 0

    def _get_avg_profit(self, profit_records):
        return round(float(np.mean([p.profit for p in profit_records])), 3) if profit_records else 0

    def _get_stdev_profit(self, profit_records):
        return round(float(np.std([p.profit for p in profit_records])), 3) if profit_records else 0

    def _get_stat(self, profit_records):
        return (self._get_total_profit(profit_records), self._get_min_profit(profit_records), self._get_max_profit(profit_records), self._get_avg_profit(profit_records), self._get_stdev_profit(profit_records), len(profit_records), )

    def _get_corrcoef(self, a, b):
        if not a:
            return 0
        return round(np.corrcoef(np.array(a), np.array(b))[0][1], 2)

    def _profit_records_to_str(self, profit_records):
        t_p, min_p, max_p, avg_p, stdev_p, l = self._get_stat(profit_records)
        profits = [p.profit for p in profit_records]
        prices = [p.price_snapshot_enter.price for p in profit_records]
        min_quantities = [p.price_snapshot_enter.min_quantity for p in profit_records]
        avg_quantities = [p.price_snapshot_enter.avg_quantity for p in profit_records]
        coef_price = self._get_corrcoef(profits, prices)
        coef_min_quantities = self._get_corrcoef(profits, min_quantities)
        coef_avg_quantities = self._get_corrcoef(profits, avg_quantities)

        return '{l} trading decisions, total: {tp}, min: {mnp}, max: {mxp}, avg: {avp}, stdev: {stdp}, corrcoef: (price: {p_coef}, min_q: {min_q_coef}, avg_q: {avg_q_coef})'.format(
            l=l, tp=t_p, mnp=min_p, mxp=max_p, avp=avg_p, stdp=stdev_p, p_coef=coef_price, min_q_coef=coef_min_quantities, avg_q_coef=coef_avg_quantities)

    def __str__(self):
        res = []
        res.append('Long/Short: ' + self._profit_records_to_str(self.profit_records))
        res.append('Long: ' + self._profit_records_to_str([pr for pr in self.profit_records if pr.profit_position is PROFIT_POSITION.LONG]))
        res.append('Short: ' + self._profit_records_to_str([pr for pr in self.profit_records if pr.profit_position is PROFIT_POSITION.SHORT]))
        return '\n'.join(res) + '\n'

    def print_records(self):
        for p in sorted(self.profit_records, key=lambda p: p.price_snapshot_enter.epoch_seconds):
            print('record:{record}'.format(record=str(p)))
        return '\n'

    def print_cumulative_profit(self):
        profit_records_sorted = sorted(self.profit_records, key=lambda p: p.price_snapshot_enter.epoch_seconds)
        x = np.array([p.price_snapshot_exit.epoch_seconds for p in profit_records_sorted])
        if len(x) == 0:
            print('no data to plot')
            return
        if len(x) > 0: x = x - x[0]
        if len(x) > 0: x = (x / 60).astype(np.int32)
        y = np.cumsum([p.profit for p in profit_records_sorted])
        gp.plot(x, y, terminal='dumb 80,40')
