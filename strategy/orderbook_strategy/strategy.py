import util.logging
import util.time
from ingest.streaming.orderbook import Orderbook
from strategy.strategy import TradeStrategy
import util.current_time
import strategy.profit


class OrderbookTradeStrategy(TradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None):
        self.orderbook = Orderbook(symbol)
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = current_time)

    def _get_close_price(self):
        return self.orderbook.get_close_price()

    # override
    def on_orderbook_snapshot(self, orderbook_snapshot):
        self.orderbook.on_update(orderbook_snapshot)
        self.on_ingest()

    def _create_price_snapshot(self):
        cp = self._get_close_price()
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        mq = 1
        aq = 1
        price_snapshot = strategy.profit.PriceSnapshot(cp, cp, cp, epoch_seconds, mq, aq)
        return price_snapshot

    def _clear_long_position(self):
        if not self.in_long_position:
            return
        cp = self._get_close_price()
        entered = self.price_snapshot_long_enter.price
        entered_epoch_seconds = self.price_snapshot_long_enter.epoch_seconds
        price_snapshot_long_exit = self._create_price_snapshot()
        profit = strategy.profit.get_profit_long(self.price_snapshot_long_enter, price_snapshot_long_exit, round_digit=5)
        profit_record = strategy.profit.ProfitRecord(self.symbol, strategy.profit.PROFIT_POSITION.LONG, self.price_snapshot_long_enter, price_snapshot_long_exit)
        self.profit_stat.append(profit_record)

        util.logging.info('({dt_str}) clearing a long position for symbol {symbol}, profit: {profit}%, price: {price}, entered: {entered} ({entered_time})'.format(
            dt_str=self._get_datetime_str(), symbol=self.symbol, price=cp, entered=entered, entered_time=util.time.epoch_seconds_to_str(entered_epoch_seconds), profit=profit * 100))
        super()._clear_long_position()

    def _clear_short_position(self):
        if not self.in_short_position:
            return
        cp = self._get_close_price()
        entered = self.price_snapshot_short_enter.price
        entered_epoch_seconds = self.price_snapshot_short_enter.epoch_seconds
        price_snapshot_short_exit = self._create_price_snapshot()
        profit = strategy.profit.get_profit_short(self.price_snapshot_short_enter, price_snapshot_short_exit, round_digit=5)
        profit_record = strategy.profit.ProfitRecord(self.symbol, strategy.profit.PROFIT_POSITION.SHORT, self.price_snapshot_short_enter, price_snapshot_short_exit)
        self.profit_stat.append(profit_record)

        util.logging.info('({dt_str}) clearing a short position for symbol {symbol}, profit: {profit}%, price: {price}, entered: {entered} ({entered_time})'.format(
            dt_str=self._get_datetime_str(), symbol=self.symbol, price=cp, entered=entered, entered_time=util.time.epoch_seconds_to_str(entered_epoch_seconds), profit=profit * 100))
        super()._clear_short_position()

    def enter_long_position(self):
        if self.in_long_position:
            return False
        util.logging.info('({dt_str}) entering a long position for symbol {symbol}, price: {price}'.format(
            dt_str=self._get_datetime_str(), symbol=self.symbol, price=self._get_close_price()))
        super().enter_long_position()

    def enter_short_position(self):
        if self.in_short_position:
            return
        util.logging.info('({dt_str}) entering a short position for symbol {symbol}, price: {price}'.format(
            dt_str=self._get_datetime_str(), symbol=self.symbol, price=self._get_close_price()))
        super().enter_short_position()

    def on_new_timebucket(self):
        pass