import os, datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')

import ingest.imports.bq
from ingest.imports.bq import EXPORT_MODE, DATASET_MODE
import ingest.imports.util
import util.symbols



ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, util.symbols.get_symbols_hotel_resort(), datetime.date(2020, 9, 8), datetime.date(2020, 9, 11), timewindow_seconds=900, out_filename='data/hotel_resort_2020_09_08_2020_09_11.csv')



