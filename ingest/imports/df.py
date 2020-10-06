import os, datetime
import numpy as np
import pandas as pd

import statsmodels
from statsmodels.tsa.stattools import coint
# just set the seed for the random number generator
np.random.seed(107)

import ingest.imports.bq
from ingest.imports.util import EXPORT_MODE, DATASET_MODE
import ingest.imports.util

def get_dataframe(dataset_mode, export_mode, symbols, start_epoch_seconds, end_epoch_seconds, timewindow_seconds):
    filename = ingest.imports.util.get_imported_file_name(dataset_mode, export_mode, symbols, start_epoch_seconds, end_epoch_seconds, timewindow_seconds)
    if not os.path.exists(filename):
        ingest.imports.bq.import_symbol_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, symbols, start_epoch_seconds, end_epoch_seconds, timewindow_seconds=timewindow_seconds)
    df = pd.read_csv(filename, names=['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
    return df
