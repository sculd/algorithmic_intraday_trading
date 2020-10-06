import os, datetime, csv
from google.cloud import bigquery
from ingest.imports.util import EXPORT_MODE, DATASET_MODE
import ingest.imports.util
import pytz

_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
_DATASET_ID_EQUITY = 'market_data'
_DATASET_ID_FOREX = 'market_data_forex'
_DATASET_ID_BINANCE = 'market_data_binance'
_DATASET_ID_PAIRTRADING_AIRLINE = 'pair_trading_airline'
_DATASET_ID_PAIRTRADING_OIL_GAS = 'pair_trading_oil_gas'
_DATASET_ID_PAIRTRADING_HOTEL_RESORT = 'pair_trading_hotel_resort'
_DATASET_ID_PAIRTRADING_RESTAURANT = 'pair_trading_restaurant'
_TABLE_ID_BY_MINUTE = 'by_minute'
_TABLE_ID_RAW = 'raw'

def get_full_table_id(dataset_mode, export_mode):
    ds_id = _DATASET_ID_EQUITY
    if dataset_mode is DATASET_MODE.EQUITY:
        ds_id = _DATASET_ID_EQUITY
    elif dataset_mode is DATASET_MODE.FOREX:
        ds_id = _DATASET_ID_FOREX
    elif dataset_mode is DATASET_MODE.BINANCE:
        ds_id = _DATASET_ID_BINANCE
    elif dataset_mode is DATASET_MODE.PAIRTRADING_AIRLINE:
        ds_id = _DATASET_ID_PAIRTRADING_AIRLINE
    elif dataset_mode is DATASET_MODE.PAIRTRADING_OIL_GAS:
        ds_id = _DATASET_ID_PAIRTRADING_OIL_GAS
    elif dataset_mode is DATASET_MODE.PAIRTRADING_HOTEL_RESORT:
        ds_id = _DATASET_ID_PAIRTRADING_HOTEL_RESORT
    elif dataset_mode is DATASET_MODE.PAIRTRADING_RESTAURANT:
        ds_id = _DATASET_ID_PAIRTRADING_RESTAURANT

    t_id = _TABLE_ID_BY_MINUTE
    if export_mode is EXPORT_MODE.BY_MINUTE:
        t_id = _TABLE_ID_BY_MINUTE
    elif export_mode is EXPORT_MODE.BY_SECOND:
        t_id = _TABLE_ID_BY_MINUTE
    elif export_mode is EXPORT_MODE.RAW:
        t_id = _TABLE_ID_RAW
    return '{p}.{d}.{t}'.format(p=_PROJECT_ID, d=ds_id, t=t_id)

_QUERY_TEMPLATE = """
    SELECT
      *
    FROM
      `{table_name}`
    WHERE
      TRUE
      {timestamp_clause}
      {symbol_clause}
    ORDER BY
      timestamp ASC
        """
_MINUTE_AGGREGATION_QUERY_TEMPLATE = """
    WITH RAW AS (
    SELECT
      *
    FROM
      `{table_name}`
    WHERE
      TRUE
      {timestamp_clause}
      {symbol_clause}
    ),
    
    BASETABLE AS (
    SELECT
      TIMESTAMP_SECONDS(UNIX_SECONDS(timestamp) - (mod(UNIX_SECONDS(timestamp), {timewindow_seconds}))) AS timestamp, symbol,  MAX(high) AS high, MIN(low) AS low, SUM(volume) AS volume
    FROM
      RAW
    WHERE
      TRUE
      {timestamp_clause}
      {symbol_clause}
    GROUP BY timestamp, symbol
    ORDER BY
      timestamp ASC
    ),
    
    FIRST_SECONDS AS (
    SELECT
      TIMESTAMP_SECONDS(UNIX_SECONDS(timestamp) - (mod(UNIX_SECONDS(timestamp), {timewindow_seconds}))) AS timestamp, symbol, MIN(timestamp) AS min_t
    FROM
      RAW
    WHERE
      TRUE
      {symbol_clause}
    GROUP BY timestamp, symbol
    ORDER BY
      timestamp ASC
    ),
    
    LAST_SECONDS AS (
    SELECT
      TIMESTAMP_SECONDS(UNIX_SECONDS(timestamp) - (mod(UNIX_SECONDS(timestamp), {timewindow_seconds}))) AS timestamp, symbol, MAX(timestamp) AS max_t
    FROM
      RAW
    WHERE
      TRUE
      {symbol_clause}
    GROUP BY timestamp, symbol
    ORDER BY
      timestamp ASC
    ),
    
    CLOSES AS (
    SELECT
      TIMESTAMP_SECONDS(UNIX_SECONDS(RAW.timestamp) - (mod(UNIX_SECONDS(RAW.timestamp), {timewindow_seconds}))) AS timestamp, RAW.symbol, AVG(RAW.close) AS close
    FROM
      RAW JOIN LAST_SECONDS ON 
      TIMESTAMP_SECONDS(UNIX_SECONDS(RAW.timestamp) - (mod(UNIX_SECONDS(RAW.timestamp), {timewindow_seconds}))) = LAST_SECONDS.timestamp AND RAW.timestamp = LAST_SECONDS.max_t AND RAW.symbol = LAST_SECONDS.symbol
    WHERE
      TRUE
    GROUP BY timestamp, RAW.symbol
    ),
    
    OPEN AS (
    SELECT
      TIMESTAMP_SECONDS(UNIX_SECONDS(RAW.timestamp) - (mod(UNIX_SECONDS(RAW.timestamp), {timewindow_seconds}))) AS timestamp, RAW.symbol, AVG(RAW.open) AS open
    FROM
      RAW JOIN FIRST_SECONDS ON 
      TIMESTAMP_SECONDS(UNIX_SECONDS(RAW.timestamp) - (mod(UNIX_SECONDS(RAW.timestamp), {timewindow_seconds}))) = FIRST_SECONDS.timestamp AND RAW.timestamp = FIRST_SECONDS.min_t AND RAW.symbol = FIRST_SECONDS.symbol
    WHERE
      TRUE
    GROUP BY timestamp, RAW.symbol
    ),
    
    OHLV AS (
    SELECT
      BASETABLE.timestamp AS timestamp, BASETABLE.symbol, OPEN.open, high, low, volume
    FROM
      BASETABLE JOIN OPEN ON 
      BASETABLE.timestamp = OPEN.timestamp AND BASETABLE.symbol = OPEN.symbol
    WHERE
      TRUE
    ),
    
    OHLCV AS (
    SELECT
      OHLV.timestamp AS timestamp, OHLV.symbol, open, high, low, CLOSES.close, volume
    FROM
      OHLV JOIN CLOSES ON 
      OHLV.timestamp = CLOSES.timestamp AND OHLV.symbol = CLOSES.symbol
    WHERE
      TRUE
    )
    
    SELECT *
    FROM OHLCV
    ORDER BY timestamp ASC

"""

def _get_query_template(export_mode):
    query_template = _QUERY_TEMPLATE
    if export_mode is EXPORT_MODE.BY_MINUTE:
        query_template = _MINUTE_AGGREGATION_QUERY_TEMPLATE
    elif export_mode is EXPORT_MODE.BY_SECOND:
        query_template = _QUERY_TEMPLATE
    elif export_mode is EXPORT_MODE.RAW:
        query_template = _QUERY_TEMPLATE
    return query_template

def _get_timestamp_clause(start_epoch_seconds, end_epoch_seconds):
    return 'AND timestamp >= TIMESTAMP_SECONDS({s}) and timestamp < TIMESTAMP_SECONDS({e})'.format(s=start_epoch_seconds, e=end_epoch_seconds)

def _get_symbol_clause(symbols):
    if not symbols:
        return ''
    return 'AND (' + ' OR '.join(map(lambda symbol: '(symbol = "{s}")'.format(s=symbol), symbols)) + ')'

_client = None

def get_big_query_client():
  global _client
  if _client is None:
      project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
      _client = bigquery.Client(project = project_id)
  return _client

def _get_rows_from_bq_query(query_str):
    print(query_str)
    bq_client = get_big_query_client()
    query_result = bq_client.query(query_str).result()
    return query_result

_IMPORT_FILE_NAME_TEMPLATE = 'data/{source}_{mode}_{symbol}_{start}_to_{end}.csv'

def _write_bq_rows_to_csv(bq_rows, csv_file):
    with open(csv_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in bq_rows:
            print(row)
            csv_writer.writerow(row.values())

def import_symbol_range(dataset_mode, export_mode, symbol, start_epoch_seconds, end_epoch_seconds, timewindow_seconds=60):
    query_template = _get_query_template(export_mode)

    query_str = query_template.format(
        table_name=get_full_table_id(dataset_mode, export_mode),
        timewindow_seconds=timewindow_seconds,
        timestamp_clause=_get_timestamp_clause(start_epoch_seconds, end_epoch_seconds),
        symbol_clause=_get_symbol_clause(symbol))
    bq_rows = _get_rows_from_bq_query(query_str)
    _write_bq_rows_to_csv(bq_rows, ingest.imports.util.get_imported_file_name(dataset_mode, export_mode, symbol, start_epoch_seconds, end_epoch_seconds, timewindow_seconds))

def import_range(dataset_mode, export_mode, start_epoch_seconds, end_epoch_seconds, timewindow_seconds=60):
    import_symbol_range(dataset_mode, export_mode, None, start_epoch_seconds, end_epoch_seconds, timewindow_seconds=timewindow_seconds)

def combine_import_market_hour_symbol_date_range(dataset_mode, export_mode, symbol, start_date, end_date, timewindow_seconds=60, out_filename = None):
    d = start_date
    filenames = []
    '''
    while d <= end_date:
        start_t = pytz.utc.localize(datetime.datetime.combine(d, datetime.time(13, 30, 0)))
        end_t = pytz.utc.localize(datetime.datetime.combine(d, datetime.time(20, 00, 0)))
        start_epoch_seconds, end_epoch_seconds = int(start_t.timestamp()), int(end_t.timestamp())
        import_symbol_range(dataset_mode, export_mode, symbol, start_epoch_seconds, end_epoch_seconds, timewindow_seconds=timewindow_seconds)
        filenames.append(ingest.imports.util.get_imported_file_name(dataset_mode, export_mode, symbol, start_epoch_seconds, end_epoch_seconds, timewindow_seconds))
        d += datetime.timedelta(days=1)
    '''
    start_t = pytz.utc.localize(datetime.datetime.combine(start_date, datetime.time(13, 30, 0)))
    end_t = pytz.utc.localize(datetime.datetime.combine(end_date, datetime.time(20, 00, 0)))
    start_epoch_seconds, end_epoch_seconds = int(start_t.timestamp()), int(end_t.timestamp())
    import_symbol_range(dataset_mode, export_mode, symbol, start_epoch_seconds, end_epoch_seconds, timewindow_seconds=timewindow_seconds)
    filenames.append(ingest.imports.util.get_imported_file_name(dataset_mode, export_mode, symbol, start_epoch_seconds, end_epoch_seconds, timewindow_seconds))

    out_filename = out_filename if out_filename else ingest.imports.util.get_combined_import_market_hour_filename(dataset_mode, export_mode, symbol, start_date, end_date, timewindow_seconds)
    with open(out_filename, 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)

def combine_import_market_hour_date_range(dataset_mode, export_mode, start_date, end_date, timewindow_seconds=60, out_filename = None):
    combine_import_market_hour_symbol_date_range(dataset_mode, export_mode, None, start_date, end_date, timewindow_seconds=timewindow_seconds, out_filename = out_filename)





