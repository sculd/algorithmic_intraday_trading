import util.logging
import util.time
from strategy.strategy import POSITION_MODE
from strategy.bar_with_times_strategy.strategy import BarWithTimesTradeStrategy
import util.current_time
import strategy.profit


class GapTradeStrategyParameter:
    def __init__(self,
                 gap_threshold_long,
                 gap_threshold_short,
                 holding_seconds_long,
                 holding_seconds_short
                 ):
        self.gap_threshold_long = gap_threshold_long
        self.gap_threshold_short = gap_threshold_short
        self.holding_seconds_long = holding_seconds_long
        self.holding_seconds_short = holding_seconds_short

def get_strategy_param():
    param = GapTradeStrategyParameter(
        -0.05,
        0.05,
        15 * 60,
        15 * 60
    )
    return param

class GapTradeStrategy(BarWithTimesTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, market_price, prev_day_close, current_time = None):
        self.market_price = market_price
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = current_time)
        self.prev_day_close = prev_day_close
        self.param = get_strategy_param()
        self.first_trade_done = False

    def on_daily_trade_start(self):
        self.first_trade_done = False

    def _get_close_price(self):
        return self.market_price.get_price(self.symbol)

    def on_gap(self, gap):
        util.logging.info('non-zero gap {g} for {symbol} is observed'.format(g=gap, symbol=self.symbol))
        new_position_mode = POSITION_MODE.NO_POSITION
        if gap > self.param.gap_threshold_short:
            new_position_mode = POSITION_MODE.SHORT_ENTERED
        elif gap < self.param.gap_threshold_long:
            new_position_mode = POSITION_MODE.LONG_ENTERED
        self._update_position_mode(new_position_mode)

    # override
    def on_trade(self, trade):
        self.aggregation.on_trade(trade)
        self.on_ingest()
        if self.first_trade_done:
            return

        #util.logging.error('First trade for {symbol}'.format(symbol=self.symbol))
        self.first_trade_done = True
        prev_close = self.prev_day_close.get(self.symbol)
        cur_quote = trade.price

        if prev_close == 0:
            #util.logging.error('Prev day close is 0 for {symbol}'.format(symbol=self.symbol))
            return

        gap = 1.0 * (cur_quote - prev_close) / prev_close
        if gap == -1:
            #util.logging.error('The gap is -1 for {symbol}'.format(symbol=self.symbol))
            return

        self.on_gap(gap)

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
        current_epoch_seconds = self.current_time.get_current_epoch_seconds()
        dt_str = self._get_datetime_str()
        cp = self._get_close_price()

        if self.position_mode is POSITION_MODE.LONG_ENTERED:
            seconds_since_long_position_enter = current_epoch_seconds - self.price_snapshot_long_enter.epoch_seconds
            util.logging.debug('({dt_str}) on_new_timebucket, seconds since entering long for {symbol}: {sec}, price: {cp}, entered: {entered}'.format(
                dt_str=dt_str, symbol=self.symbol, sec=seconds_since_long_position_enter, cp=cp, entered=self.price_snapshot_long_enter.price))
            if seconds_since_long_position_enter >= self.param.holding_seconds_long:
                util.logging.info("For {symbol} leaving a long position for timing out. Seconds since enter: {seconds}".format(
                    symbol = self.symbol,
                    seconds = seconds_since_long_position_enter
                ))
                self._update_position_mode(POSITION_MODE.NO_POSITION)

        if self.position_mode is POSITION_MODE.SHORT_ENTERED:
            seconds_since_short_position_enter = current_epoch_seconds - self.price_snapshot_short_enter.epoch_seconds
            util.logging.debug('({dt_str}) on_new_timebucket, seconds since entering short for {symbol}: {sec}, price: {cp}, entered: {entered}'.format(
                dt_str=dt_str, symbol=self.symbol, sec=seconds_since_short_position_enter, cp=cp, entered=self.price_snapshot_short_enter.price))
            if seconds_since_short_position_enter >= self.param.holding_seconds_short:
                util.logging.info("For {symbol} leaving a short position for timing out. Seconds since enter: {seconds}".format(
                    symbol = self.symbol,
                    seconds = seconds_since_short_position_enter
                ))
                self._update_position_mode(POSITION_MODE.NO_POSITION)
