import os, datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')

from google.cloud import bigquery

_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
_DATASET_ID_EQUITY = 'daily_market_data_equity'
_TABLE_ID_DAILY = 'daily'
_FULL_TABLE_ID = '{p}.{d}.{t}'.format(p=_PROJECT_ID, d=_DATASET_ID_EQUITY, t=_TABLE_ID_DAILY)
_WRITE_QUEUE_SIZE_THRESHOLD = 4000
_POLYGON_API_KEY = os.environ['API_KEY_POLYGON']
_FINNHUB_API_KEY = os.environ['API_KEY_FINNHUB']

_bigquery_client = None

def get_big_query_client():
  global _bigquery_client
  if _bigquery_client is None:
      project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
      _bigquery_client = bigquery.Client(project = project_id)
  return _bigquery_client

from polygon import RESTClient
from google.cloud.bigquery.table import Row

_polygon_client = RESTClient(_POLYGON_API_KEY)

def _get_daily_aggregate_results(date_str):
    resp = _polygon_client.stocks_equities_grouped_daily("us", "stocks", date_str)
    results = resp.results
    return results

def _write_rows(rows):
    if not rows:
        return
    i = 0
    bq_client = get_big_query_client()
    while True:
        bq_client.insert_rows(bq_client.get_table(_FULL_TABLE_ID), rows[i:i + _WRITE_QUEUE_SIZE_THRESHOLD])
        i += _WRITE_QUEUE_SIZE_THRESHOLD
        if i >= len(rows):
            break

def _export_results(results):
    def _result_to_row(result):
        vw = result['vw'] if 'vw' in result else None
        return Row(
            (datetime.date.fromtimestamp(int(result['t'] / 1000.0)), result['T'].encode("ascii", "ignore").decode(), result['o'], result['h'], result['l'], result['c'], result['v'], vw),
            {c: i for i, c in enumerate(['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'volume_weighted_price'])}
        )

    rows = [_result_to_row(result) for result in results]
    _write_rows(rows)

import csv
def _results_to_csv_rows(results):
    def _result_to_csv_row(result):
        vw = result['vw'] if 'vw' in result else None
        return (datetime.date.fromtimestamp(int(result['t'] / 1000.0)), result['T'], result['o'], result['h'], result['l'], result['c'], result['v'], vw, )

    csv_rows = [_result_to_csv_row(result) for result in results]
    return csv_rows


def _get_daily_aggregate_csv_rows(date_str):
    with open("data/daily/daily_{dt_str}.csv".format(dt_str=date_str), newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        return list([row for row in csv_reader])

def _csv_rows_to_bq_rows(csv_rows):
    def _to_vq_row(csv_row):
        return Row(
            (datetime.date.fromisoformat(csv_row[0]), csv_row[1], float(csv_row[2]), float(csv_row[3]), float(csv_row[4]), float(csv_row[5]), float(csv_row[6]), float(csv_row[7])),
            {c: i for i, c in enumerate(['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'volume_weighted_price'])}
        )

    return [_to_vq_row(r) for r in csv_rows]

def _export_csv_rows(csv_rows):
    def _to_vq_row(csv_row):
        return Row(
            (datetime.date.fromisoformat(csv_row[0]), csv_row[1], float(csv_row[2]), float(csv_row[3]), float(csv_row[4]), float(csv_row[5]), float(csv_row[6]), float(csv_row[7])),
            {c: i for i, c in enumerate(['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'volume_weighted_price'])}
        )
    rows = [_to_vq_row(csv_row) for csv_row in csv_rows]
    _write_rows(rows)


def export_daily_aggregate(date_str):
    csv_rows = _get_daily_aggregate_csv_rows(date_str)
    _export_csv_rows(csv_rows)


'''
recent_date = datetime.date(2020, 8, 11)
#oldest_date = datetime.date(2005, 1, 1)
oldest_date = datetime.date(2008, 6, 17)

date = oldest_date
while True:
    print('exporting for', date)
    date_str = str(date)
    try:
        export_daily_aggregate(str(date))
    except Exception as ex:
        print(ex)
    date += datetime.timedelta(days=1)
    if date > recent_date:
        break
#'''

'''
recent_date = datetime.date(2020, 8, 11)
oldest_date = datetime.date(2005, 1, 1)

date = recent_date
while True:
    print('exporting for', date)
    date_str = str(date)
    #export_daily_aggregate(str(date))
    results = _get_daily_aggregate_results(date_str)
    csv_rows_for_date = _results_to_csv_rows(results)

    with open('data/daily/daily_{d}.csv'.format(d=date_str), 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in csv_rows_for_date:
            csv_writer.writerow(row)

    date -= datetime.timedelta(days=1)
    if date < oldest_date:
        break
#'''

#'''
with open('data/daily_snp500/agg/daily.csv', 'w') as of:
    of.write('date,symbol,open,high,low,close,volume,volume_weighted_price\n')
    for i, f in enumerate(sorted(list(os.listdir('data/daily_snp500')))):
        if '.csv' not in f: continue
        print(i, f)
        for line in open('data/daily_snp500/' + f, 'r'):
            if len(line.split(',')) < 8:
                print('invalid row', line)
            of.write(line)
#'''

'''
for line in open('data/daily/agg/daily.csv', 'r'):
    if len(line.split(',')) < 8:
        print('invalid row', line)
    line_ascii = line.encode("ascii", "ignore").decode()
    if len(line_ascii) != len(line):
        print('row with non-ascii', line)
'''

'''
with open('data/daily/agg/daily.csv', 'w') as of:
    for line in open('data/daily/agg/temp.csv', 'r'):
        if len(line.split(',')) < 8:
            print('invalid row', line)
        line_ascii = line.encode("ascii", "ignore").decode()
        if len(line_ascii) != len(line):
            print('row with non-ascii', line)
        of.write(line_ascii)
'''

'''
from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket('stock_daily_data')
blob = bucket.blob('daily.csv')

blob.upload_from_filename('data/daily/agg/daily.csv')
'''



'''
resp = _polygon_client.stocks_equities_grouped_daily("us", "stocks", "2006-08-14")
results = resp.results
print(len(results))
'''

import finnhub


finnhub_client = finnhub.Client(api_key=_FINNHUB_API_KEY)
print(finnhub_client.indices_const(symbol = "^GSPC"))


#'''
recent_date = datetime.date(2020, 8, 11)
oldest_date = datetime.date(2005, 1, 1)
constituents = {}
import csv
with open("data/daily/constituent/historical_components.csv", newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in csv_reader:
        date_str = row[0]
        if date_str == 'date':
            continue
        constituents[date_str] = set(row[1].split(','))

date = oldest_date
prev_date = date
while True:
    if str(date) not in constituents and str(prev_date) in constituents:
        constituents[str(date)] = constituents[str(prev_date)]
    prev_date = date
    date += datetime.timedelta(days=1)
    if date > recent_date:
        break
#'''

'''
recent_date = datetime.date(2020, 8, 11)
oldest_date = datetime.date(2005, 1, 1)
import csv
date = oldest_date
while True:
    if date > recent_date:
        break
    date_str = str(date)
    print(date_str)
    if date_str not in constituents:
        date += datetime.timedelta(days=1)
        continue
    if not os.path.exists("data/daily/daily_{dt}.csv".format(dt=date_str)):
        continue
    with open("data/daily_snp500/daily_{dt}.csv".format(dt=date_str), 'w') as of:
        for line in open("data/daily/daily_{dt}.csv".format(dt=date_str), newline=''):
            line_symbol = line.split(',')[1]
            if line_symbol not in constituents[date_str]:
                continue
            of.write(line)

    date += datetime.timedelta(days=1)
#'''
