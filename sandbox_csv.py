from ingest.streaming.sudden_move.trend_reversal.crypto import BinanceCsvFileRun

if __name__ == '__main__':
    trade_run = BinanceCsvFileRun(
        'data/binance.sorted.minute.csv',
        {} # 'DASHUSDT', 'ZECUSDT', 'BANDUSDT', 'HCUSDT'
    )
