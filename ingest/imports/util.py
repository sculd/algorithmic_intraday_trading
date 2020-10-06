import datetime
_IMPORT_FILE_NAME_TEMPLATE = 'data/{source}_{mode}{ta}_window{w}_{symbol}_{start}_to_{end}.csv'
_COMBINE_IMPORT_FILE_NAME_TEMPLATE = 'data/combined_{source}_{mode}_window{w}_{symbol}_{start}_to_{end}.csv'

from enum import Enum

class EXPORT_MODE(Enum):
    BY_SECOND = 1
    BY_MINUTE = 2
    RAW = 3

class DATASET_MODE(Enum):
    EQUITY = 1
    FOREX = 2
    BINANCE = 3
    PAIRTRADING_AIRLINE = 4
    PAIRTRADING_OIL_GAS = 5
    PAIRTRADING_HOTEL_RESORT = 6
    PAIRTRADING_RESTAURANT = 7

def from_iso_to_epoch_seconds(iso_datetime_str):
    '''
    example: 2020-07-24 14:00:00+00:00
    :param iso_datetime_str:
    :return:
    '''
    return int(datetime.datetime.fromisoformat(iso_datetime_str).timestamp())

def market_open_epoch_seconds(year, month, day):
    return from_iso_to_epoch_seconds('{y}-{m}-{d} 13:30:00+00:00'.format(y=year, m=month, d=day))

def market_close_epoch_seconds(year, month, day):
    return from_iso_to_epoch_seconds('{y}-{m}-{d} 20:00:00+00:00'.format(y=year, m=month, d=day))

def _dataset_mode_to_str(dataset_mode):
    source = ''
    if dataset_mode is DATASET_MODE.EQUITY:
        source = 'stock'
    elif dataset_mode is DATASET_MODE.FOREX:
        source = 'forex'
    elif dataset_mode is DATASET_MODE.BINANCE:
        source = 'binance'
    elif dataset_mode is DATASET_MODE.PAIRTRADING_AIRLINE:
        source = 'airline'
    elif dataset_mode is DATASET_MODE.PAIRTRADING_OIL_GAS:
        source = 'oilgas'
    elif dataset_mode is DATASET_MODE.PAIRTRADING_HOTEL_RESORT:
        source = 'hotelresort'
    elif dataset_mode is DATASET_MODE.PAIRTRADING_RESTAURANT:
        source = 'restaurant'
    return source

def get_imported_file_name(dataset_mode, export_mode, symbols, start_epoch_seconds, end_epoch_seconds, timewindow_seconds):
    source = _dataset_mode_to_str(dataset_mode)

    return _IMPORT_FILE_NAME_TEMPLATE.format(
        source=source,
        mode='raw' if export_mode is EXPORT_MODE.RAW else ('second' if export_mode is EXPORT_MODE.BY_SECOND else 'minute'),
        ta='',
        symbol='ALL' if not symbols else ','.join(symbols),
        w=timewindow_seconds,
        start=datetime.datetime.fromtimestamp(start_epoch_seconds),
        end=datetime.datetime.fromtimestamp(end_epoch_seconds)
    )

def get_imported_with_ta_file_name(dataset_mode, export_mode, symbols, start_epoch_seconds, end_epoch_seconds, timewindow_seconds):
    source = _dataset_mode_to_str(dataset_mode)

    return _IMPORT_FILE_NAME_TEMPLATE.format(
        source=source,
        mode='raw' if export_mode is EXPORT_MODE.RAW else ('second' if export_mode is EXPORT_MODE.BY_SECOND else 'minute'),
        ta='_ta',
        symbol='ALL' if not symbols else ','.join(symbols),
        w=timewindow_seconds,
        start=datetime.datetime.fromtimestamp(start_epoch_seconds),
        end=datetime.datetime.fromtimestamp(end_epoch_seconds)
    )

def get_combined_import_market_hour_filename(dataset_mode, export_mode, symbols, start_date, end_date, timewindow_seconds):
    source = ''
    if dataset_mode is DATASET_MODE.EQUITY:
        source = 'stock'
    elif dataset_mode is DATASET_MODE.FOREX:
        source = 'forex'
    elif dataset_mode is DATASET_MODE.BINANCE:
        source = 'binance'
    elif dataset_mode is DATASET_MODE.PAIRTRADING_AIRLINE:
        source = 'airline'
    elif dataset_mode is DATASET_MODE.PAIRTRADING_OIL_GAS:
        source = 'oilgas'
    elif dataset_mode is DATASET_MODE.PAIRTRADING_HOTEL_RESORT:
        source = 'hotelresort'
    elif dataset_mode is DATASET_MODE.PAIRTRADING_RESTAURANT:
        source = 'restaurant'

    return _COMBINE_IMPORT_FILE_NAME_TEMPLATE.format(
        source=source,
        mode='raw' if export_mode is EXPORT_MODE.RAW else ('second' if export_mode is EXPORT_MODE.BY_SECOND else 'minute'),
        symbol='ALL' if not symbols else ','.join(symbols),
        w=timewindow_seconds,
        start=str(start_date),
        end=str(end_date)
    )



