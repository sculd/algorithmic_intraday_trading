import market.tradier.history
import market.tradier.price
import util.symbols
import util.logging as logging

_h = market.tradier.history.History()

class PrevDayCloses:
    def __init__(self):
        self.last_update_date_str = ''
        self.prev_day_closes = {}

    def _update_symbol(self, symbol):
        days_delta = 1
        prev_close = _h.get_prev_day_close(symbol, days_delta=days_delta + 1)
        self.prev_day_closes[symbol] = prev_close
        return prev_close

    def update(self):
        logging.info("updating prev day closes")
        symbols = util.symbols.get_symbols_snp500()
        cnt_valid_updates = 0
        cnt_total_updates = 0
        for symbol in symbols:
            if self._update_symbol(symbol) != 0:
                cnt_valid_updates += 1
            cnt_total_updates += 1
        logging.info("updated prev day closes, total_updates: {cnt_total_updates}, valid_updates: {cnt_valid_updates}".format(
            cnt_total_updates=cnt_total_updates, cnt_valid_updates=cnt_valid_updates))


    def get(self, symbol):
        return self.prev_day_closes[symbol] if symbol in self.prev_day_closes else 0




