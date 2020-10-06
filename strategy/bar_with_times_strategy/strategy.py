import util.logging
import util.time
from ingest.streaming.aggregation import Aggregation
from strategy.strategy import TradeStrategy, TradeStrategyParameter
import util.current_time
import strategy.profit

_STOP_LOSS_THRESHOLD = 0.04
_HARD_STOP_LOSS_THRESHOLD = 0.10
_MIN_QUANTITY_WINDOW_MINUTES = 10
_LOCAL_MIN_MAX_WINDOW_SECONDS = 60 * 10

class BarWithTimesTradeStrategyParameter(TradeStrategyParameter):
    def __init__(self,
                 stop_loss_threshold,
                 hard_stop_loss_threshold,
                 min_quantity_window_minutes,
                 local_min_max_window_seconds
                 ):
        super().__init__(stop_loss_threshold, hard_stop_loss_threshold)
        self.min_quantity_window_minutes = min_quantity_window_minutes
        self.local_min_max_window_seconds = local_min_max_window_seconds

def get_bar_with_times_trade_strategy_parameter():
    return BarWithTimesTradeStrategyParameter(_STOP_LOSS_THRESHOLD, _HARD_STOP_LOSS_THRESHOLD, _MIN_QUANTITY_WINDOW_MINUTES, _LOCAL_MIN_MAX_WINDOW_SECONDS)

class BarWithTimesTradeStrategy(TradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None):
        self.aggregation = Aggregation(symbol)
        self.param = get_bar_with_times_trade_strategy_parameter()
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = current_time, param = self.param)

    def _get_if_long_stop_loss_crossed(self):
        return self._get_close_price() <= self._get_long_stop_loss_price()

    def _get_if_long_hard_stop_loss_crossed(self):
        return self._get_close_price() <= self._get_long_hard_stop_loss_price()

    def _get_if_short_stop_loss_crossed(self):
        return self._get_close_price() >= self._get_short_stop_loss_price()

    def _get_if_short_hard_stop_loss_crossed(self):
        return self._get_close_price() >= self._get_short_hard_stop_loss_price()

    def _get_close_price(self):
        return self.aggregation._get_close_price()

    def _get_max_high_price(self, time_window_minutes):
        return self.aggregation._get_max_high_price(time_window_minutes)

    def _get_min_low_price(self, time_window_minutes):
        return self.aggregation._get_min_low_price(time_window_minutes)

    # override
    def on_trade(self, trade):
        self.aggregation.on_trade(trade)
        self.on_ingest()

    # override
    def on_bar_with_time(self, bar_with_time):
        self.aggregation.on_bar_with_time(bar_with_time)
        self.on_ingest()

    def _create_price_snapshot(self):
        cp = self._get_close_price()
        max_p = self._get_max_high_price(self.param.local_min_max_window_seconds // 60)
        min_p = self._get_min_low_price(self.param.local_min_max_window_seconds // 60)
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        mq = self.aggregation.get_minimal_quantity(self.param.min_quantity_window_minutes, drop_last=True)
        aq = self.aggregation.get_avg_quantity(self.param.min_quantity_window_minutes, drop_last=True)
        price_snapshot = strategy.profit.PriceSnapshot(cp, max_p, min_p, epoch_seconds, mq, aq)
        return price_snapshot

    def _clear_long_position(self):
        if not self.in_long_position:
            return
        cp = self._get_close_price()
        entered = self.price_snapshot_long_enter.price
        entered_epoch_seconds = self.price_snapshot_long_enter.epoch_seconds
        price_snapshot_long_exit = self._create_price_snapshot()
        profit = strategy.profit.get_profit_long(self.price_snapshot_long_enter, price_snapshot_long_exit)
        profit_record = strategy.profit.ProfitRecord(self.symbol, strategy.profit.PROFIT_POSITION.LONG, self.price_snapshot_long_enter, price_snapshot_long_exit)
        self.profit_stat.append(profit_record)

        util.logging.info('({dt_str}) clearing a long position for symbol {symbol}, profit: {profit}, price: {price}, entered: {entered} ({entered_time}), min quantity over {m} minutes: {q}, avg quantity: {aq}'.format(
            dt_str=self._get_datetime_str(), symbol=self.symbol, price=cp, entered=entered, entered_time=util.time.epoch_seconds_to_str(entered_epoch_seconds), profit=profit, m=self.param.min_quantity_window_minutes,
            q=self.aggregation.get_minimal_quantity(self.param.min_quantity_window_minutes, drop_last=True), aq=self.aggregation.get_avg_quantity(self.param.min_quantity_window_minutes)))
        super()._clear_long_position()

    def _clear_short_position(self):
        if not self.in_short_position:
            return
        cp = self._get_close_price()
        entered = self.price_snapshot_short_enter.price
        entered_epoch_seconds = self.price_snapshot_short_enter.epoch_seconds
        price_snapshot_short_exit = self._create_price_snapshot()
        profit = strategy.profit.get_profit_short(self.price_snapshot_short_enter, price_snapshot_short_exit)
        profit_record = strategy.profit.ProfitRecord(self.symbol, strategy.profit.PROFIT_POSITION.SHORT, self.price_snapshot_short_enter, price_snapshot_short_exit)
        self.profit_stat.append(profit_record)

        util.logging.info('({dt_str}) clearing a short position for symbol {symbol}, profit: {profit}, price: {price}, entered: {entered} ({entered_time}), min quantity over {m} minutes: {q}, avg quantity: {aq}'.format(
            dt_str=self._get_datetime_str(), symbol=self.symbol, price=cp, entered=entered, entered_time=util.time.epoch_seconds_to_str(entered_epoch_seconds), profit=profit, m=self.param.min_quantity_window_minutes,
            q=self.aggregation.get_minimal_quantity(self.param.min_quantity_window_minutes, drop_last=True), aq=self.aggregation.get_avg_quantity(self.param.min_quantity_window_minutes)))
        super()._clear_short_position()

    def enter_long_position(self):
        if self.in_long_position:
            return False
        util.logging.info('({dt_str}) entering a long position for symbol {symbol}, price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq}'.format(
            dt_str=self._get_datetime_str(), symbol=self.symbol, price=self._get_close_price(), m=self.param.min_quantity_window_minutes,
            q=self.aggregation.get_minimal_quantity(self.param.min_quantity_window_minutes, drop_last=True), aq=self.aggregation.get_avg_quantity(self.param.min_quantity_window_minutes)))
        super().enter_long_position()

    def enter_short_position(self):
        if self.in_short_position:
            return
        util.logging.info('({dt_str}) entering a short position for symbol {symbol}, price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq}'.format(
            dt_str=self._get_datetime_str(), symbol=self.symbol, price=self._get_close_price(), m=self.param.min_quantity_window_minutes,
            q=self.aggregation.get_minimal_quantity(self.param.min_quantity_window_minutes, drop_last=True), aq=self.aggregation.get_avg_quantity(self.param.min_quantity_window_minutes)))
        super().enter_short_position()
