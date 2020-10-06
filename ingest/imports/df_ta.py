import os, datetime
import numpy as np
import pandas as pd
from ta import add_all_ta_features
from ta.utils import dropna

import ingest.imports.bq
from ingest.imports.util import EXPORT_MODE, DATASET_MODE
import ingest.imports.util

def apply_dataframe_ta(df):
    df_ta = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume").drop(['trend_psar_up', 'trend_psar_down'], axis=1).dropna()
    return df_ta

def get_dataframe_with_ta(dataset_mode, export_mode, symbol, start_epoch_seconds, end_epoch_seconds, timewindow_seconds):
    symbols = [symbol]
    filename = ingest.imports.util.get_imported_file_name(dataset_mode, export_mode, symbols, start_epoch_seconds, end_epoch_seconds, timewindow_seconds)
    if not os.path.exists(filename):
        ingest.imports.bq.import_symbol_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, symbols, start_epoch_seconds, end_epoch_seconds, timewindow_seconds=timewindow_seconds)
    df = pd.read_csv(filename, names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
    df_s = df.set_index(['datetime', 'symbol']).xs(symbol, level=1)
    df_ta = add_all_ta_features(df_s, open="open", high="high", low="low", close="close", volume="volume").drop(['trend_psar_up', 'trend_psar_down'], axis=1).dropna()
    filename_ta = ingest.imports.util.get_imported_with_ta_file_name(dataset_mode, export_mode, symbols, start_epoch_seconds, end_epoch_seconds, timewindow_seconds)
    df_ta.to_csv(filename_ta)

    return df_ta
