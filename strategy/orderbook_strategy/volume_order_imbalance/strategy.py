import util.logging
import util.time
from strategy.strategy import POSITION_MODE
from strategy.orderbook_strategy.strategy import OrderbookTradeStrategy
from strategy.factors.orderbook_factors.volume_order_imbalance import VolumeOrderImbalance, VolumeOrderImbalanceParameter

_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 60 * 1
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 60 * 1
_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 10
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 10

def get_factor_param():
    param = VolumeOrderImbalanceParameter()
    return param

class VolumeOrderImbalanceStrategyParameter:
    def __init__(self,
                 short_position_timeout_seconds,
                 long_position_timeout_seconds,
                 minimum_short_position_hold_seconds,
                 minimum_long_position_hold_seconds,
                 ):
        self.short_position_timeout_seconds = short_position_timeout_seconds
        self.long_position_timeout_seconds = long_position_timeout_seconds
        self.minimum_short_position_hold_seconds = minimum_short_position_hold_seconds
        self.minimum_long_position_hold_seconds = minimum_long_position_hold_seconds

def get_strategy_param():
    param = VolumeOrderImbalanceStrategyParameter(
        _SHORT_POSITION_TIMEOUT_SECONDS,
        _LONG_POSITION_TIMEOUT_SECONDS,
        _MINIMUM_SHORT_POSITION_HOLD_SECONDS,
        _MINIMUM_LONG_POSITION_HOLD_SECONDS
    )
    return param

class VolumeOrderImbalanceStrategy(OrderbookTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None):
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=current_time)
        factor_map = {'voi': VolumeOrderImbalance(symbol, self.orderbook, get_factor_param())}
        self.factor_map = factor_map
        self.param = get_strategy_param()
        self.long_count, self.short_count = 0, 0

    def on_new_timebucket(self):
        current_epoch_seconds = self.current_time.get_current_epoch_seconds()
        dt_str = self._get_datetime_str()
        cp = self._get_close_price()

        if self.position_mode is POSITION_MODE.LONG_ENTERED:
            seconds_since_long_position_enter = current_epoch_seconds - self.price_snapshot_long_enter.epoch_seconds
            util.logging.debug('({dt_str}) on_new_timebucket, seconds since entering long for {symbol}: {sec}, price: {cp}, entered: {entered}'.format(
                dt_str=dt_str, symbol=self.symbol, sec=seconds_since_long_position_enter, cp=cp, entered=self.price_snapshot_long_enter.price))
            if seconds_since_long_position_enter >= self.param.long_position_timeout_seconds:
                util.logging.info("For {symbol} leaving a long position for timing out. Seconds since enter: {seconds}".format(
                    symbol = self.symbol,
                    seconds = seconds_since_long_position_enter
                ))
                self._update_position_mode(POSITION_MODE.NO_POSITION)

        if self.position_mode is POSITION_MODE.SHORT_ENTERED:
            seconds_since_short_position_enter = current_epoch_seconds - self.price_snapshot_short_enter.epoch_seconds
            util.logging.debug('({dt_str}) on_new_timebucket, seconds since entering short for {symbol}: {sec}, price: {cp}, entered: {entered}'.format(
                dt_str=dt_str, symbol=self.symbol, sec=seconds_since_short_position_enter, cp=cp, entered=self.price_snapshot_short_enter.price))
            if seconds_since_short_position_enter >= self.param.short_position_timeout_seconds:
                util.logging.info("For {symbol} leaving a short position for timing out. Seconds since enter: {seconds}".format(
                    symbol = self.symbol,
                    seconds = seconds_since_short_position_enter
                ))
                self._update_position_mode(POSITION_MODE.NO_POSITION)

    def update_position_mode_on_ingest(self):
        new_position_mode = self.position_mode
        current_epoch_seconds = self.current_time.get_current_epoch_seconds()
        cp = self._get_close_price()

        voi = self.factor_map['voi'].get()

        print('voi: ', voi)

        if self.position_mode is POSITION_MODE.NO_POSITION:
            if voi > 150:
                new_position_mode = POSITION_MODE.LONG_ENTERED
            elif voi < -150:
                new_position_mode = POSITION_MODE.SHORT_ENTERED

        elif self.position_mode is POSITION_MODE.LONG_ENTERED:
            seconds_since_long_position_enter = current_epoch_seconds - self.price_snapshot_long_enter.epoch_seconds
            if cp <= self.long_stop_loss_price and seconds_since_long_position_enter >= self.param.minimum_long_position_hold_seconds:
                util.logging.info("For {symbol}, leaving a long position for crossing the stop loss. long_stop_loss_price: {long_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, long_stop_loss_price=round(self.long_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp <= self.long_hard_stop_loss_price:
                util.logging.info("For {symbol}, leaving a long position for crossing the hard stop loss. long_hard_stop_loss_price: {long_hard_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, long_hard_stop_loss_price=round(self.long_hard_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp >= self.long_stop_loss_reset_price:
                self._setup_long_stop_loss()

        elif self.position_mode is POSITION_MODE.SHORT_ENTERED:
            seconds_since_short_position_enter = current_epoch_seconds - self.price_snapshot_short_enter.epoch_seconds
            if cp >= self.short_stop_loss_price and seconds_since_short_position_enter >= self.param.minimum_short_position_hold_seconds:
                util.logging.info("For {symbol}, leaving a short position for crossing the stop loss. short_stop_loss_price: {short_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, short_stop_loss_price=round(self.short_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp >= self.short_hard_stop_loss_price:
                util.logging.info("For {symbol}, leaving a short position for crossing the hard stop loss. short_hard_stop_loss_price: {short_hard_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, short_hard_stop_loss_price=round(self.short_hard_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp <= self.short_stop_loss_reset_price:
                self._setup_short_stop_loss()

        self._update_position_mode(new_position_mode)



