from collections import deque

_SNAPSHOT_EXPORT_DEPTH = 3

class OrderbookSnapshot:
    def __init__(self, symbol):
        self.symbol = symbol

        self.epoch_seconds = 0

        # descending order
        self.bid_prices = []
        self.bid_sizes = []

        # ascending order
        self.ask_prices = []
        self.ask_sizes = []

    def get_bid_price(self):
        '''
        Gets the highest bid price
        '''
        return self.bid_prices[0] if len(self.bid_prices) > 0 else 0

    def get_bid_volume(self):
        '''
        Gets the highest bid volume
        '''
        return self.bid_sizes[0] if len(self.bid_sizes) > 0 else 0

    def get_ask_price(self):
        '''
        Gets the lowest bid price
        '''
        return self.ask_prices[0] if len(self.ask_prices) > 0 else 0

    def get_ask_volume(self):
        '''
        Gets the lowest bid volume
        '''
        return self.ask_sizes[0] if len(self.ask_sizes) > 0 else 0

    @staticmethod
    def get_tuple_names():
        return ['epoch_seconds', 'symbol'] + \
               ['bid_price_{i}'.format(i=i) for i in range(_SNAPSHOT_EXPORT_DEPTH)] + \
               ['bid_volume_{i}'.format(i=i) for i in range(_SNAPSHOT_EXPORT_DEPTH)] + \
               ['ask_price_{i}'.format(i=i) for i in range(_SNAPSHOT_EXPORT_DEPTH)] + \
               ['ask_volume_{i}'.format(i=i) for i in range(_SNAPSHOT_EXPORT_DEPTH)]

    def to_tuple(self):
        bid_prizes, bid_volumes = [], []
        for i in range(_SNAPSHOT_EXPORT_DEPTH):
            if len(self.bid_prices)-1 < i:
                bid_prizes.append(self.bid_prices[-1])
                bid_volumes.append(0)
            else:
                bid_prizes.append(self.bid_prices[i])
                bid_volumes.append(self.bid_sizes[i])

        ask_prizes, ask_volumes = [], []
        for i in range(_SNAPSHOT_EXPORT_DEPTH):
            if len(self.ask_prices)-1 < i:
                ask_prizes.append(self.ask_prices[-1])
                ask_volumes.append(0)
            else:
                ask_prizes.append(self.ask_prices[i])
                ask_volumes.append(self.ask_sizes[i])

        return [int(self.epoch_seconds), self.symbol] + bid_prizes + bid_volumes + ask_prizes + ask_volumes

    def __str__(self):
        return 'symbol: {symbol}, epoch_seconds: {epoch_seconds}, bid_price: {bid_price}, bid_volume: {bid_volume}, ask_price: {ask_price}, ask_volume: {ask_volume}'.format(
            symbol = self.symbol,
            epoch_seconds = self.epoch_seconds,
            bid_price = self.get_bid_price(),
            bid_volume = self.get_bid_volume(),
            ask_price = self.get_ask_price(),
            ask_volume = self.get_ask_volume()
        )

class OrderbookSnapshots:
    def __init__(self, symbol):
        self.symbol = symbol
        self.snapshots = deque()

    def add(self, snapshot):
        self.snapshots.append(snapshot)

    def append_to_csv_file(self, csv_file, epoch_seconds_start, epoch_seconds_end):
        while len(self.snapshots) > 0:
            snapshot = self.snapshots.popleft()
            epoch_seconds = int(snapshot.epoch_seconds)
            if epoch_seconds_start is not None and epoch_seconds < epoch_seconds_start:
                print('skipping as the timestamp {t} is before the bucket {bt}'.format(t=epoch_seconds, bt=epoch_seconds_start))
                continue
            if epoch_seconds_end is not None and epoch_seconds > epoch_seconds_end:
                print('skipping as the timestamp {t} is after the bucket {bt}'.format(t=epoch_seconds, bt=epoch_seconds_end))
                break
            csv_file.write(','.join(map(lambda v: str(v), snapshot.to_tuple())) + '\n')


class Orderbook:
    def __init__(self, symbol):
        self.snapshot = OrderbookSnapshot(symbol)
        self.prev_snapshot = OrderbookSnapshot(symbol)

    def on_update(self, snapshot):
        self.prev_snapshot = self.snapshot
        self.snapshot = snapshot

    def get_close_price(self):
        b_len, a_len = len(self.snapshot.bid_prices), len(self.snapshot.ask_prices)
        if b_len == 0 and a_len == 0:
            return 0
        elif a_len == 0:
            return self.snapshot.bid_prices[0]
        elif b_len == 0:
            return self.snapshot.ask_prices[0]
        else:
            return (self.snapshot.bid_prices[0] + self.snapshot.ask_prices[0]) / 2.0

