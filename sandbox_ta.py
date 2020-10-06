import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')

import pandas as pd
import ingest.imports.df_ta
import ingest.imports.util
from ingest.imports.bq import EXPORT_MODE, DATASET_MODE


#df = pd.read_csv('data/binance_minute_window60_CRVUSDT_2020-09-12 17:00:00_to_2020-09-20 16:00:00.csv', names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])

#df = ingest.imports.df_ta.get_dataframe_with_ta(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, 'JPM', ingest.imports.util.from_iso_to_epoch_seconds('2020-09-14 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-14 20:00:00+00:00'), 60)

df = pd.read_csv('data/binance_minute_window60_ETHUSDT_2020-08-12 17:00:00_to_2020-09-20 16:00:00.csv', names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])

df_ta = ingest.imports.df_ta.apply_dataframe_ta(df)


df_ta.to_csv('data/binance_ta_minute_window60_ETHUSDT_2020-08-12 17:00:00_to_2020-09-20 16:00:00.csv')

print('done')



