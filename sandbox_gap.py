import datetime, pprint, time, os
import pandas as pd
import pytz

import market.tradier.history

h = market.tradier.history.History()
print(h.get_prev_day_close('AWK', days_delta=2))
print(h.get_prev_day_open('AWK', days_delta=1))

import market.tradier.price

p = market.tradier.price.Price()
print(p.get_price('AWK'))

import finnhub

# Configure API key
configuration = finnhub.Configuration(
    api_key={
        'token': os.getenv('FINNHUB_API_KEY')
    }
)

finnhub_client = finnhub.DefaultApi(finnhub.ApiClient(configuration))
#print(finnhub_client.stock_candles('AAPL', '1', 1593097200, 1593097380))

import market.finnhub.history

fh = market.finnhub.history.History()
'''
print(fh.get_prev_day_intraday_close('AAPL', days_delta=2, minutes_delta=0))
print(fh.get_prev_day_intraday_close('AAPL', days_delta=2, minutes_delta=15))
'''

'''
import ingest.daily_gap

#days_delta=2
gap_moves = []

for days_delta in range(2,20):
    picks = ingest.daily_gap.daily_pick(days_delta=days_delta)
    print('days_delta', days_delta, len(picks), ' picks')
    day_str = fh._get_prev_day_datetime(days_delta)

    for pick in picks:
        p_open, p_15, p_30 = fh.get_prev_day_intraday_early_closes(pick.symbol, days_delta=days_delta)
        if p_open == 0:
            continue
        change_15 = (p_15 - p_open) / p_open
        change_30 = (p_30 - p_open) / p_open
        gap_moves.append((day_str, pick.symbol, pick.gap, pick.threshold, change_15, change_30,))
        time.sleep(1)


import pickle
pickle.dump(gap_moves, open('picks_gap', 'wb'))
#'''

import pickle
gap_moves = pickle.load(open('picks_gap', 'rb'))


import numpy as np
import matplotlib.pyplot as plt

gap_moves_plots = [g for g in gap_moves if g[2] > -0.1 and g[4] > -0.1]
plt.scatter([g[2] for g in gap_moves_plots], [g[4] for g in gap_moves_plots])

plt.xlim(-0.15, 0.15)
plt.ylim(-0.15, 0.15)

plt.show()


for g in gap_moves:
    if g[3] < -0.05:
        print(g)
