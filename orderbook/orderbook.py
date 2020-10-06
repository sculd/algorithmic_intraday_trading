class Spread:
    def __init__(self, book):
        self.bid, self.ask = 0, 0
        self.spread = 0
        self.spread_ratio = 0

    def to_debug_string(self):
        return '(Spread) dummy bid: 0, ask: 0, spread: 0, spread_ratio: 0'

class BookThickness:
    def __init__(self, book):
        self.volume_bids, self.volume_asks = 0, 0

    def to_debug_string(self):
        return '(BookThickness) dummy volume_bids: 0, volume_asks: 0'

class OrderBook:
    def __init__(self, symbol):
        self.symbol = symbol
        self._update()

    def _update(self):
        self.spread = Spread(None)
        self.book_thickness = BookThickness(None)

    def to_debug_string(self):
        return '(OrderBook) dummy symbol: {symbol}, spread: 0, thickness: 0'
