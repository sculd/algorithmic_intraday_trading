import util.logging
import util.time
from strategy.strategy import POSITION_MODE
from strategy.factors.bar_with_times_factors.sudden_move import PRICE_MOVE_MODE, SHORT_TERM_PRICE_MOVE_MODE
from strategy.factors.bar_with_times_factors.sudden_move import SuddenMove, SuddenMoveParameter
from strategy.bar_with_times_strategy.sudden_move.strategy import SuddenMoveTradeStrategy, SuddenMoveTradeStrategyParameter

_CHANGE_THRESHOLD_JUMP = 0.1
_CHANGE_THRESHOLD_DROP = -0.1
_CHANGE_THRESHOLD_FROM_SEEKING_TO_ENTRY = 0.08
_IGNORE_CHANGE_BEYOND_THIS_MAGNITUDE = 0.5
_PRICE_LOWER_BOUND_LONG = 5.0
_PRICE_LOWER_BOUND_SHORT = 5.0
_PRICE_UPPER_BOUND = 200.0
_CHANGE_WINDOW_MINUTE = 10
_CHANGE_WINDOW_MINUTE_SHORT = 5

_STOP_LOSS_THRESHOLD = 0.04
_HARD_STOP_LOSS_THRESHOLD = 0.06
_SHORT_POSITION_TIMEOUT_SECONDS = 60 * 30
_LONG_POSITION_TIMEOUT_SECONDS = 60 * 20
_MINIMUM_SHORT_POSITION_HOLD_SECONDS = 60 * 10
_MINIMUM_LONG_POSITION_HOLD_SECONDS = 60 * 15
_QUANTITY_WINDOW_MINUTES = 10
_SEEKING_ENTRY_EXPIRE_SECONDS = 60 * 20
_LOCAL_MIN_MAX_WINDOW_SECONDS = 60 * 10
_TRADING_VOLUME_UPPER_BOUND_LONG = None
_TRADING_VOLUME_LOWER_BOUND_LONG = 100000
_TRADING_VOLUME_UPPER_BOUND_SHORT = None
_TRADING_VOLUME_LOWER_BOUND_SHORT = 100000

def get_strategy_param():
    param = SuddenMoveTradeStrategyParameter(
        _STOP_LOSS_THRESHOLD,
        _HARD_STOP_LOSS_THRESHOLD,
        _SHORT_POSITION_TIMEOUT_SECONDS,
        _LONG_POSITION_TIMEOUT_SECONDS,
        _MINIMUM_SHORT_POSITION_HOLD_SECONDS,
        _MINIMUM_LONG_POSITION_HOLD_SECONDS,
        _QUANTITY_WINDOW_MINUTES,
        _SEEKING_ENTRY_EXPIRE_SECONDS,
        _LOCAL_MIN_MAX_WINDOW_SECONDS,
        _CHANGE_THRESHOLD_FROM_SEEKING_TO_ENTRY,
        -1 * _CHANGE_THRESHOLD_FROM_SEEKING_TO_ENTRY,
        _TRADING_VOLUME_UPPER_BOUND_LONG,
        _TRADING_VOLUME_LOWER_BOUND_LONG,
        _TRADING_VOLUME_UPPER_BOUND_SHORT,
        _TRADING_VOLUME_LOWER_BOUND_SHORT,
        _PRICE_LOWER_BOUND_LONG,
        _PRICE_LOWER_BOUND_SHORT,
        _PRICE_UPPER_BOUND
    )
    return param

class SuddenMoveTrendReversalTradeStrategy(SuddenMoveTradeStrategy):
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None):
        super().__init__(positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time=current_time)
        self.param = get_strategy_param()
        factor_map = {'SuddenMove': SuddenMove(symbol, self.aggregation, self.get_factor_param())}

    def get_factor_param(self):
        param = SuddenMoveParameter(
            _CHANGE_THRESHOLD_JUMP,
            _CHANGE_THRESHOLD_DROP,
            _IGNORE_CHANGE_BEYOND_THIS_MAGNITUDE,
            min(_PRICE_LOWER_BOUND_LONG, _PRICE_LOWER_BOUND_SHORT),
            _CHANGE_WINDOW_MINUTE,
            _CHANGE_WINDOW_MINUTE_SHORT
        )
        return param

    def check_spread_for_seeking_position(self):
        spr = self.long_enter.market_price.get_bidask_spread(self.symbol)
        if abs(spr) > 0.03:
            util.logging.debug("for {symbol} a long term move was observed but the spread is too large. spread (ask - bid) / bid: {spr}, at {t}".format(
                    symbol=self.symbol, spr=spr,
                    t=self.aggregation.get_latest_time()))
            return False
        return True

    def check_param_for_long(self):
        cp = self._get_close_price()
        quantity_minutes = self.param.quantity_window_minutes
        min_quantity_minutes = self.aggregation.get_minimal_quantity(quantity_minutes, drop_last=True)
        avg_quantity_minutes = self.aggregation.get_avg_quantity(quantity_minutes, drop_last=False)
        if self.param.trading_quantity_lower_bound_long is not None and avg_quantity_minutes < self.param.trading_quantity_lower_bound_long:
            util.logging.debug("for {symbol} long term drop move was observed but not enough volume. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        elif self.param.trading_quantity_upper_bound_long is not None and avg_quantity_minutes > self.param.trading_quantity_upper_bound_long:
            util.logging.debug("for {symbol} long term drop move was observed but volume is too high. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        elif self.param.price_lower_bound_long is not None and cp < self.param.price_lower_bound_long:
            util.logging.debug("for {symbol} long term drop move was observed but the price is too low. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        elif self.param.price_upper_bound is not None and cp > self.param.price_upper_bound:
            util.logging.debug("for {symbol} long term drop move was observed but the price is too high. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        elif self.long_count > 2:
            util.logging.debug("for {symbol} long term drop move was observed but the long count ({lc}) for the day exceeds the limit. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, lc=self.long_count, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        return True

    def check_param_for_short(self):
        cp = self._get_close_price()
        quantity_minutes = self.param.quantity_window_minutes
        min_quantity_minutes = self.aggregation.get_minimal_quantity(quantity_minutes, drop_last=True)
        avg_quantity_minutes = self.aggregation.get_avg_quantity(quantity_minutes, drop_last=False)
        if self.param.trading_quantity_lower_bound_short is not None and avg_quantity_minutes < self.param.trading_quantity_lower_bound_short:
            util.logging.debug("for {symbol} long term jump move was observed but not enough volume. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        elif self.param.trading_quantity_upper_bound_short is not None and avg_quantity_minutes > self.param.trading_quantity_upper_bound_short:
            util.logging.debug("for {symbol} long term jump move was observed but volume is too high. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        elif self.param.price_lower_bound_short is not None and cp < self.param.price_lower_bound_short:
            util.logging.debug("for {symbol} long term jump move was observed but the price is too low. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        elif self.param.price_upper_bound is not None and cp > self.param.price_upper_bound:
            util.logging.debug("for {symbol} long term jump move was observed but the price is too high. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        elif self.short_count > 2:
            util.logging.debug("for {symbol} long term jump move was observed but the short count ({sc}) for the day exceeds the limit. price: {price}, min quantity over {m} minutes: {q}, avg quantity: {aq} at {t}".format(
                    symbol=self.symbol, sc=self.short_count, price=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes, t=self.aggregation.get_latest_time()))
            return False
        return True

    def update_position_mode_on_ingest(self):
        market_signal, short_term_market_signal = self.factor_map['SuddenMove'].get()

        new_position_mode = self.position_mode
        dt_str = self._get_datetime_str()
        current_epoch_seconds = self.current_time.get_current_epoch_seconds()

        if new_position_mode is not self.position_mode:
            util.logging.info('position mode change from {f} to {t}'.format(f=self.position_mode, t=new_position_mode))

        cp = self._get_close_price()
        quantity_minutes = self.param.quantity_window_minutes
        min_quantity_minutes = self.aggregation.get_minimal_quantity(quantity_minutes, drop_last=True)
        avg_quantity_minutes = self.aggregation.get_avg_quantity(quantity_minutes, drop_last=False)

        if self.position_mode is POSITION_MODE.LONG_ENTERED:
            seconds_since_long_position_enter = current_epoch_seconds - self.price_snapshot_long_enter.epoch_seconds
            if cp > self.highest_price_in_long_position:
                self.highest_price_in_long_position = cp
                print('updated highest_price_in_long_position: {p}, long_stop_loss_price: {sp}, long_hard_stop_loss_price: {hsp}'.format(p=cp, sp=self._get_long_stop_loss_price(), hsp=self._get_long_hard_stop_loss_price()))

            if self._get_if_long_stop_loss_crossed() and seconds_since_long_position_enter >= self.param.minimum_long_position_hold_seconds:
                util.logging.info("For {symbol}, leaving a long position for crossing the stop loss. long_stop_loss_price: {long_stop_loss_price}, current_price: {cp}, min quantity over {m} minutes: {q}, avg quantity: {aq}".format(
                    symbol=self.symbol, long_stop_loss_price=round(self.long_stop_loss_price, 3),
                    cp=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif self._get_if_long_hard_stop_loss_crossed():
                util.logging.info("For {symbol}, leaving a long position for crossing the hard stop loss. long_hard_stop_loss_price: {long_hard_stop_loss_price}, current_price: {cp}, min quantity over {m} minutes: {q}, avg quantity: {aq}".format(
                    symbol=self.symbol, long_hard_stop_loss_price=round(self.long_hard_stop_loss_price, 3),
                    cp=cp, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp >= self.long_stop_loss_reset_price:
                self._setup_long_stop_loss()

        elif self.position_mode is POSITION_MODE.SHORT_ENTERED:
            seconds_since_short_position_enter = current_epoch_seconds - self.price_snapshot_short_enter.epoch_seconds
            if cp < self.lowest_price_in_short_position:
                self.lowest_price_in_short_position = cp
                print('updated lowest_price_in_short_position: {p}, short_stop_loss_price: {sp}, short_hard_stop_loss_price: {hsp}'.format(p=cp, sp=self._get_short_stop_loss_price(), hsp=self._get_short_hard_stop_loss_price()))

            if self._get_if_short_stop_loss_crossed() and seconds_since_short_position_enter >= self.param.minimum_short_position_hold_seconds:
                util.logging.info("For {symbol}, leaving a short position for crossing the stop loss. short_stop_loss_price: {short_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, short_stop_loss_price=round(self.short_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif self._get_if_short_hard_stop_loss_crossed():
                util.logging.info("For {symbol}, leaving a short position for crossing the hard stop loss. short_hard_stop_loss_price: {short_hard_stop_loss_price}, current_price: {cp}".format(
                    symbol=self.symbol, short_hard_stop_loss_price=round(self.short_hard_stop_loss_price, 3),
                    cp=cp
                ))
                new_position_mode = POSITION_MODE.NO_POSITION
            elif cp <= self.short_stop_loss_reset_price:
                self._setup_short_stop_loss()
        else:
            if self.position_mode is POSITION_MODE.LONG_SEEKING_ENTRY:
                self.min_price_seeking_long_entry = min(self.min_price_seeking_long_entry, cp)
            elif self.position_mode is POSITION_MODE.SHORT_SEEKING_ENTRY:
                self.max_price_seeking_short_entry = max(self.max_price_seeking_short_entry, cp)

            if market_signal is PRICE_MOVE_MODE.DROP_SIGNAL:
                if self.check_param_for_long() and self.check_spread_for_seeking_position():
                    new_position_mode = POSITION_MODE.LONG_SEEKING_ENTRY
            elif market_signal is PRICE_MOVE_MODE.JUMP_SIGNAL:
                if self.check_param_for_short() and self.check_spread_for_seeking_position():
                    new_position_mode = POSITION_MODE.SHORT_SEEKING_ENTRY

            if self.position_mode is POSITION_MODE.LONG_SEEKING_ENTRY:
                util.logging.debug("({dt_str}) seeking for long entry {symbol}. price: {price}".format(dt_str=dt_str, symbol=self.symbol, price=cp))

                enter_by_short_term_move_mode = short_term_market_signal is SHORT_TERM_PRICE_MOVE_MODE.JUMP_SIGNAL
                local_min_price = min(self.min_price_seeking_long_entry, self.price_snapshot_long_seeking_entry.local_min_price)
                change_since_seeking_entry = (cp - local_min_price) / local_min_price
                enter_by_move_away = change_since_seeking_entry > self.param.change_threshold_from_seeking_to_entry_long
                enter = enter_by_short_term_move_mode or enter_by_move_away
                expired = current_epoch_seconds - self.price_snapshot_long_seeking_entry.epoch_seconds > self.param.seeking_entry_expire_seconds

                if expired:
                    util.logging.info("({dt_str}) entry seeking expired{symbol}".format(dt_str=dt_str, symbol=self.symbol))
                    new_position_mode = POSITION_MODE.NO_POSITION

                elif not enter:
                    util.logging.info("({dt_str}) no entry found yet {symbol}".format(dt_str=dt_str, symbol=self.symbol))

                elif enter:
                    util.logging.info("({dt_str}) found long position entry point {symbol} with short term market signal: {s_signal}, long term: {l_signal}, min quantity over {m} minutes: {q}, avg quantity: {aq}".format(
                        dt_str=dt_str, symbol=self.symbol, s_signal=short_term_market_signal, l_signal=market_signal, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes))
                    if enter_by_move_away:
                        util.logging.info("({dt_str}) long position entry point {symbol} by moving away, change_since_seeking_entry: {cs}".format(
                                dt_str=dt_str, symbol=self.symbol, cs=change_since_seeking_entry))

                    new_position_mode = POSITION_MODE.LONG_ENTERED
                    self._setup_long_stop_loss()

            elif self.position_mode is POSITION_MODE.SHORT_SEEKING_ENTRY:
                util.logging.debug("({dt_str}) seeking for short entry {symbol}. price: {price}".format(dt_str=dt_str, symbol=self.symbol, price=cp))

                enter_by_short_term_move_mode = short_term_market_signal is SHORT_TERM_PRICE_MOVE_MODE.DROP_SIGNAL
                local_max_price = max(self.max_price_seeking_short_entry, self.price_snapshot_short_seeking_entry.local_max_price)
                change_since_seeking_entry = (cp - local_max_price) / local_max_price
                enter_by_move_away = change_since_seeking_entry < self.param.change_threshold_from_seeking_to_entry_short
                enter = enter_by_short_term_move_mode or enter_by_move_away
                expired = current_epoch_seconds - self.price_snapshot_short_seeking_entry.epoch_seconds > self.param.seeking_entry_expire_seconds

                if expired:
                    util.logging.info("({dt_str}) entry seeking expired{symbol}".format(dt_str=dt_str, symbol=self.symbol))
                    new_position_mode = POSITION_MODE.NO_POSITION

                elif not enter:
                    util.logging.info("({dt_str}) no entry found yet {symbol}".format(dt_str=dt_str, symbol=self.symbol))

                elif enter:
                    util.logging.info("({dt_str}) found short position entry point {symbol} with short term market signal: {s_signal}, long term: {l_signal}, min quantity over {m} minutes: {q}, avg quantity: {aq}".format(
                        dt_str=dt_str, symbol=self.symbol, s_signal=short_term_market_signal, l_signal=market_signal, q=min_quantity_minutes, aq=avg_quantity_minutes, m=quantity_minutes))
                    if enter_by_move_away:
                        util.logging.info("({dt_str}) short position entry point {symbol} by moving away, change_since_seeking_entry: {cs}".format(
                                dt_str=dt_str, symbol=self.symbol, cs=change_since_seeking_entry))
                    new_position_mode = POSITION_MODE.SHORT_ENTERED
                    self._setup_short_stop_loss()

        self._update_position_mode(new_position_mode)
        self.prev_market_signal = market_signal

