import os
import numpy as np
import pandas as pd
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')

import statsmodels
from statsmodels.tsa.stattools import coint
# just set the seed for the random number generator
np.random.seed(107)

import datetime
import matplotlib.pyplot as plt
import ingest.imports.df
import ingest.imports.util
from ingest.imports.bq import EXPORT_MODE, DATASET_MODE


def get_coint_score_pvalue(table, symbol1, symbol2):
    Y = table[[symbol1]].rename(columns={symbol1: "value"})
    X = table[[symbol2]].rename(columns={symbol2: "value"})
    score, pvalue, _ = coint(X, Y)
    return score, pvalue


df = pd.read_csv('data/combined_oilgas_minute_window900_ALL_2020-06-01_to_2020-08-31.csv', names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
dftest = pd.read_csv(ingest.imports.util.get_imported_file_name(DATASET_MODE.PAIRTRADING_OIL_GAS, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-11 20:00:00+00:00'), timewindow_seconds=60), names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
df1 = pd.read_csv(ingest.imports.util.get_imported_file_name(DATASET_MODE.PAIRTRADING_OIL_GAS, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 20:00:00+00:00'), timewindow_seconds=60), names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])

max_len = 0
dropped_symbols = []
for symbol in df.symbol.unique():
    l = len(df[df.symbol == symbol])
    max_len = max(max_len, l)
    if l < max_len // 2:
        print('{s}, {l}'.format(s=symbol, l=l))
        dropped_symbols.append(symbol)

for symbol in dropped_symbols:
    df = df[df.symbol != symbol]

df_pivot = df.pivot(index='datetime', columns='symbol', values='close').fillna(method='ffill')
df_corr = df_pivot.corr()

high_corr_pairs = []
for symbol, row in df_corr.iterrows():
    for s, corr in row.items():
        if symbol == s: continue
        if corr < 0.9: continue
        if (s, symbol, corr,) in high_corr_pairs: continue
        high_corr_pairs.append((symbol, s, corr,))


high_corr_pairs_coint = []
for pair in high_corr_pairs:
    print(pair)
    t_score, pvalue = get_coint_score_pvalue(df_pivot, pair[0], pair[1])
    high_corr_pairs_coint.append(pair + (t_score, pvalue, ))

high_corr_pairs_coint = sorted(high_corr_pairs_coint, key = lambda p: p[3])
print(high_corr_pairs_coint[:5])



def get_ratio(df, symbol1, symbol2):
    table = pd.pivot_table(df, values='close', index=['datetime'], columns=['symbol'], aggfunc=np.sum)[[symbol1, symbol2]].dropna()
    Y = table[[symbol1]].rename(columns={symbol1: "value"})
    X = table[[symbol2]].rename(columns={symbol2: "value"})
    return Y / X

def get_ratio_mean(df, symbol1, symbol2):
    ratio = get_ratio(df, symbol1, symbol2)
    mean = ratio.mean()
    return mean.value

#symbol1, symbol2 = 'FANG', 'VNOM'
#symbol1, symbol2 = 'LONE', 'TRCH'
#symbol1, symbol2 = 'AXAS', 'TRCH'
#symbol1, symbol2 = 'PTEN', 'VNOM'
symbol1, symbol2 = 'PTEN', 'PVAC'

ratio = get_ratio(df, symbol1, symbol2)
plt.plot(ratio)

rolling_mean = ratio.rolling(window=60).mean()
rolling_std = ratio.rolling(window=60).std()

plt.plot(ratio)
plt.plot(rolling_mean)
plt.plot(rolling_mean + 1 * rolling_std)
plt.plot(rolling_mean - 1 * rolling_std)
plt.xlabel('Time')
plt.legend(['Price Ratio', 'Mean'])

print('done')
pass