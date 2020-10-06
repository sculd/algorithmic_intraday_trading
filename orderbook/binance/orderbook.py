import orderbook.orderbook
import market.binance.common

_THICKNESS_COEFFICIENT = 0.05

class BinanceSpread(orderbook.orderbook.Spread):
    def __init__(self, book):
        super().__init__(book)
        bids, asks = book['bids'], book['asks']
        b = 0
        if len(bids) > 0:
            b = float(bids[0][0])
        a = 0
        if len(asks) > 0:
            a = float(asks[0][0])
        self.bid, self.ask = b, a
        self.spread = round(a - b, 5)
        self.spread_ratio = round(self.spread / (a + b) * 2.0, 5)

    def to_debug_string(self):
        return '(Spread) bid: {b}, ask: {a}, spread: {s}, spread_ratio: {r}'.format(
            b=self.bid, a=self.ask, s=self.spread, r=self.spread_ratio)

class BinanceBookThickness(orderbook.orderbook.BookThickness):
    def __init__(self, book):
        super().__init__(book)
        spread = BinanceSpread(book)
        bids, asks = book['bids'], book['asks']
        vol_bids, vol_asks = 0, 0

        for b in bids:
            b_val, b_vol = float(b[0]), float(b[1])
            if b_val < spread.bid * (1.0 - _THICKNESS_COEFFICIENT):
                break
            vol_bids += b_vol * (spread.bid - b_val)
        for a in asks:
            a_val, a_vol = float(a[0]), float(a[1])
            if a_val > spread.ask * (1.0 + _THICKNESS_COEFFICIENT):
                break
            vol_asks += a_vol * (a_val - spread.ask)

        self.volume_bids, self.volume_asks = round(vol_bids, 2), round(vol_asks, 2)

    def to_debug_string(self):
        return '(BookThickness) volume_bids: {b}, volume_asks: {a}'.format(b=self.volume_bids, a=self.volume_asks)

class BinanceOrderBook(orderbook.orderbook.OrderBook):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.client = market.binance.common.get_client()
        self.symbol = symbol
        self._update()

    def _update(self):
        self.book = self.client.get_order_book(symbol=self.symbol)
        self.spread = BinanceSpread(self.book)
        self.book_thickness = BinanceBookThickness(self.book)

    def to_debug_string(self):
        return '(OrderBook) symbol: {symbol}, spread: {s}, thickness: {th}'.format(
            symbol=self.symbol, s=self.spread.to_debug_string(), th=self.book_thickness.to_debug_string())
