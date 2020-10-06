import os, datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')

'''
bar_with_time = BarWithTime(datetime.datetime.utcnow(), Bar('dummy', 5, 10, 1, 6, 100))
ingest.export.export_by_minute.export_bar_with_time(bar_with_time)
ingest.export.export_by_minute._flush_write_queue()

tarde = Trade(int(datetime.datetime.now().timestamp()), 'dummy', 10, 100)
ingest.export.export_raw.export_trade(tarde)
ingest.export.export_raw._flush_write_queue()
#'''


import ingest.imports.bq
from ingest.imports.bq import EXPORT_MODE, DATASET_MODE
import ingest.imports.util


#ingest.imports.bq.import_symbol_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['DRIO'], ingest.imports.util.from_iso_to_epoch_seconds('2020-08-06 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-08-06 20:00:00+00:00'))
#ingest.imports.bq.import_symbol_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, ['JPM', 'BAC', 'KO', 'PEP', 'JNJ', 'PG'], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 20:00:00+00:00'))
#ingest.imports.bq.import_symbol_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 20:00:00+00:00'))

#ingest.imports.bq.import_symbol_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-08 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-08 20:00:00+00:00'))
#ingest.imports.bq.import_symbol_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-09 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-09 20:00:00+00:00'))

'''
ingest.imports.bq.import_symbol_range(DATASET_MODE.BINANCE, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-01 20:00:00+00:00'))
ingest.imports.bq.import_symbol_range(DATASET_MODE.BINANCE, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-02 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-02 20:00:00+00:00'))
ingest.imports.bq.import_symbol_range(DATASET_MODE.BINANCE, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-03 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-03 20:00:00+00:00'))
ingest.imports.bq.import_symbol_range(DATASET_MODE.BINANCE, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-04 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-04 20:00:00+00:00'))
ingest.imports.bq.import_symbol_range(DATASET_MODE.BINANCE, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-08 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-08 20:00:00+00:00'))
ingest.imports.bq.import_symbol_range(DATASET_MODE.BINANCE, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-09 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-09 20:00:00+00:00'))
'''

ingest.imports.bq.import_symbol_range(DATASET_MODE.EQUITY, EXPORT_MODE.BY_MINUTE, [], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-29 13:30:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-29 20:00:00+00:00'), timewindow_seconds=60)

#ingest.imports.bq.import_symbol_range(DATASET_MODE.BINANCE, EXPORT_MODE.BY_MINUTE, ['FLMBUSD'], ingest.imports.util.from_iso_to_epoch_seconds('2020-09-28 00:00:00+00:00'), ingest.imports.util.from_iso_to_epoch_seconds('2020-09-28 23:00:00+00:00'))

'''
ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.PAIRTRADING_AIRLINE, EXPORT_MODE.BY_MINUTE, [], datetime.date(2020, 6, 1), datetime.date(2020, 8, 31), timewindow_seconds=60)
ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.PAIRTRADING_OIL_GAS, EXPORT_MODE.BY_MINUTE, [], datetime.date(2020, 6, 1), datetime.date(2020, 8, 31), timewindow_seconds=60)
ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.PAIRTRADING_HOTEL_RESORT, EXPORT_MODE.BY_MINUTE, [], datetime.date(2020, 6, 1), datetime.date(2020, 8, 31), timewindow_seconds=60)
ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.PAIRTRADING_RESTAURANT, EXPORT_MODE.BY_MINUTE, [], datetime.date(2020, 6, 1), datetime.date(2020, 8, 31), timewindow_seconds=60)
#'''


'''
ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.PAIRTRADING_AIRLINE, EXPORT_MODE.BY_MINUTE, [], datetime.date(2020, 9, 1), datetime.date(2020, 9, 11), timewindow_seconds=60)
ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.PAIRTRADING_OIL_GAS, EXPORT_MODE.BY_MINUTE, [], datetime.date(2020, 9, 1), datetime.date(2020, 9, 11), timewindow_seconds=60)
ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.PAIRTRADING_HOTEL_RESORT, EXPORT_MODE.BY_MINUTE, [], datetime.date(2020, 9, 1), datetime.date(2020, 9, 11), timewindow_seconds=60)
ingest.imports.bq.combine_import_market_hour_symbol_date_range(DATASET_MODE.PAIRTRADING_RESTAURANT, EXPORT_MODE.BY_MINUTE, [], datetime.date(2020, 9, 1), datetime.date(2020, 9, 11), timewindow_seconds=60)
#'''



