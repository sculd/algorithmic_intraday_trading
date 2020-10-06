import os
import numpy as np
import pandas as pd
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')

import statsmodels
from statsmodels.tsa.stattools import coint
# just set the seed for the random number generator
np.random.seed(107)

import matplotlib.pyplot as plt
import ingest.imports.df
import ingest.imports.util
from ingest.imports.bq import EXPORT_MODE, DATASET_MODE

#df = pd.read_csv('data/stock_minute_AAPL,MSFT_2020-08-07 06:30:00_to_2020-08-07 13:00:00.csv', names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
#df = pd.read_csv('data/stock_minute_JPM,BAC_2020-09-03 06:30:00_to_2020-09-03 13:00:00.csv', names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
# df = pd.read_csv('data/stock_minute_JPM,BAC,KO,PEP,JNJ,PG_2020-09-01 06:30:00_to_2020-09-01 13:00:00.csv', names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])

df = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 20:00:00+00:00'))


def get_coint_score_pvalue(df, symbol1, symbol2):
    table = pd.pivot_table(df, values='close', index=['datetime'], columns=['symbol'], aggfunc=np.sum).dropna()
    Y = table[[symbol1]].rename(columns={symbol1: "value"})
    X = table[[symbol2]].rename(columns={symbol2: "value"})
    score, pvalue, _ = coint(X, Y)
    return score, pvalue

def get_ratio(df, symbol1, symbol2):
    table = pd.pivot_table(df, values='close', index=['datetime'], columns=['symbol'], aggfunc=np.sum).dropna()
    Y = table[[symbol1]].rename(columns={symbol1: "value"})
    X = table[[symbol2]].rename(columns={symbol2: "value"})
    return Y / X

def get_ratio_mean(df, symbol1, symbol2):
    ratio = get_ratio(df, symbol1, symbol2)
    mean = ratio.mean()
    return mean.value

df24 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-08-24 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-08-24 20:00:00+00:00'))
df25 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-08-25 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-08-25 20:00:00+00:00'))
df26 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-08-26 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-08-26 20:00:00+00:00'))
df27 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-08-27 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-08-27 20:00:00+00:00'))
df28 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-08-28 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-08-28 20:00:00+00:00'))
df1 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 20:00:00+00:00'))
df2 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-02 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-02 20:00:00+00:00'))
df3 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-03 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-03 20:00:00+00:00'))
df4 = ingest.imports.df.get_dataframe(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-04 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-04 20:00:00+00:00'))

pairs = (('JPM', 'BAC'), ('KO', 'PEP'), ('JNJ', 'PG'))
for pair in pairs:
    print(pair)
    print('coint24', get_coint_score_pvalue(df24, pair[0], pair[1])[1])
    print('coint25', get_coint_score_pvalue(df25, pair[0], pair[1])[1])
    print('coint26', get_coint_score_pvalue(df26, pair[0], pair[1])[1])
    print('coint27', get_coint_score_pvalue(df27, pair[0], pair[1])[1])
    print('coint28', get_coint_score_pvalue(df28, pair[0], pair[1])[1])
    print('coint1', get_coint_score_pvalue(df1, pair[0], pair[1])[1])
    print('coint2', get_coint_score_pvalue(df2, pair[0], pair[1])[1])
    print('coint3', get_coint_score_pvalue(df3, pair[0], pair[1])[1])
    print('coint4', get_coint_score_pvalue(df4, pair[0], pair[1])[1])

for pair in pairs:
    print('pair', pair)
    print('mean24', get_ratio_mean(df24, pair[0], pair[1]))
    print('mean25', get_ratio_mean(df25, pair[0], pair[1]))
    print('mean26', get_ratio_mean(df26, pair[0], pair[1]))
    print('mean27', get_ratio_mean(df27, pair[0], pair[1]))
    print('mean28', get_ratio_mean(df28, pair[0], pair[1]))
    print('mean1', get_ratio_mean(df1, pair[0], pair[1]))
    print('mean2', get_ratio_mean(df2, pair[0], pair[1]))
    print('mean3', get_ratio_mean(df3, pair[0], pair[1]))
    print('mean4', get_ratio_mean(df4, pair[0], pair[1]))


ratio = get_ratio(df24, 'KO', 'PEP')
ratio = ratio.append(get_ratio(df25, 'KO', 'PEP'))
ratio = ratio.append(get_ratio(df26, 'KO', 'PEP'))
ratio = ratio.append(get_ratio(df27, 'KO', 'PEP'))
ratio = ratio.append(get_ratio(df28, 'KO', 'PEP'))
ratio = ratio.append(get_ratio(df1, 'KO', 'PEP'))
ratio = ratio.append(get_ratio(df2, 'KO', 'PEP'))
ratio = ratio.append(get_ratio(df3, 'KO', 'PEP'))
ratio = ratio.append(get_ratio(df4, 'KO', 'PEP'))

rolling_mean = ratio.rolling(window=60).mean()
rolling_std = ratio.rolling(window=60).std()

plt.plot(ratio)
plt.plot(rolling_mean)
plt.plot(rolling_mean + 1 * rolling_std)
plt.plot(rolling_mean - 1 * rolling_std)
plt.xlabel('Time')
plt.legend(['Price Ratio', 'Mean'])


plt.show()
print('done')


