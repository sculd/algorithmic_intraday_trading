import datetime, threading, time
import util.logging
import util.time
import market.pick
import market.pick_margin
from ingest.streaming.aggregation import Aggregation
import util.current_time
import strategy.profit
from enum import Enum

class POSITION_MODE(Enum):
    NO_POSITION = 1
    SHORT_SEEKING_ENTRY = 2
    SHORT_ENTERED = 3
    LONG_SEEKING_ENTRY = 4
    LONG_ENTERED = 5
    SEEKING_ENTRY = 6

class TRADING_ACTION(Enum):
    NO_ACTION = 1
    ENTER_LONG = 2
    EXIT_LONG = 3
    ENTER_SHORT = 4
    EXIT_SHORT = 5

TICK_TIMEBUCKET_SECONDS = 30
POSITION_UPDATE_TIMEBUCKET_SECONDS = 30

class TradeStrategyParameter:
    def __init__(self,
                 stop_loss_threshold,
                 hard_stop_loss_threshold
                 ):
        self.stop_loss_threshold = stop_loss_threshold
        self.hard_stop_loss_threshold = hard_stop_loss_threshold

_STOP_LOSS_THRESHOLD = 0.04
_HARD_STOP_LOSS_THRESHOLD = 0.10

def get_trade_strategy_parameter():
    return TradeStrategyParameter(_STOP_LOSS_THRESHOLD, _HARD_STOP_LOSS_THRESHOLD)

class TradeStrategy():
    def __init__(self, positionsize, symbol, long_enter, long_exit, short_enter, short_exit, current_time = None, param = None):
        self.param = param if param else get_trade_strategy_parameter()
        self.symbol = symbol
        self.t_now_tz = None

        self.long_enter = long_enter
        self.long_exit = long_exit
        self.short_enter = short_enter
        self.short_exit = short_exit

        self.current_time = current_time if current_time else util.current_time.CurrentTime()
        self.last_ingest_epoch_seconds = 0
        self.positionsize = positionsize
        self.position_mode = POSITION_MODE.NO_POSITION
        self.prev_position_mode = POSITION_MODE.NO_POSITION

        self.profit_stat = strategy.profit.ProfitStat(50)

        self.in_long_position = False
        self.price_snapshot_long_enter = self._create_price_snapshot()
        self.long_stop_loss_price = 0
        self.long_hard_stop_loss_price = 0  # hard stop loss does care for how long the position was held.
        self.highest_price_in_long_position = 0
        self.long_stop_loss_reset_price = 0

        self.in_short_position = False
        self.price_snapshot_short_enter = self._create_price_snapshot()
        self.short_stop_loss_price = 0
        self.short_hard_stop_loss_price = 0
        self.lowest_price_in_short_position = 0
        self.short_stop_loss_reset_price = 0

        self.factor_map = {}

        self.long_count, self.short_count = 0, 0

    def _get_long_stop_loss_price(self):
        return self.highest_price_in_long_position * (1.0 - self.param.stop_loss_threshold)

    def _get_long_hard_stop_loss_price(self):
        return self.highest_price_in_long_position * (1.0 - self.param.hard_stop_loss_threshold)

    def _get_short_stop_loss_price(self):
        return self.lowest_price_in_short_position * (1.0 + self.param.stop_loss_threshold)

    def _get_short_hard_stop_loss_price(self):
        return self.lowest_price_in_short_position * (1.0 + self.param.hard_stop_loss_threshold)

    def _get_datetime_str(self):
        return str(datetime.datetime.utcfromtimestamp(self.current_time.get_current_epoch_seconds()))

    def _get_close_price(self):
        return 0

    def _setup_long_stop_loss(self):
        cp = self._get_close_price()
        self.long_stop_loss_price = cp * (1.0 - self.param.stop_loss_threshold)
        self.long_hard_stop_loss_price = cp * (1.0 - self.param.hard_stop_loss_threshold)
        self.long_stop_loss_reset_price = cp * (1 + self.param.stop_loss_threshold)
        util.logging.info("For {symbol},  reset the long stop loss. long_stop_loss_price: {long_stop_loss_price}, long_stop_loss_reset_price: {long_stop_loss_reset_price}, long_hard_stop_loss_price: {long_hard_stop_loss_price} ({hs}), current price: {cp}, entered: {entered}".format(
            symbol=self.symbol, long_stop_loss_price = round(self.long_stop_loss_price, 3), long_stop_loss_reset_price = round(self.long_stop_loss_reset_price, 3), long_hard_stop_loss_price = round(self.long_hard_stop_loss_price, 3), hs=_HARD_STOP_LOSS_THRESHOLD, cp=cp, entered=self.price_snapshot_long_enter.price
        ))

    def _setup_short_stop_loss(self):
        cp = self._get_close_price()
        self.short_stop_loss_price = cp * (1 + self.param.stop_loss_threshold)
        self.short_hard_stop_loss_price = cp * (1 + self.param.hard_stop_loss_threshold)
        self.short_stop_loss_reset_price = cp * (1 - self.param.stop_loss_threshold)
        util.logging.info("For {symbol}, reset the short stop loss. short_stop_loss_price: {short_stop_loss_price}, short_stop_loss_reset_price: {short_stop_loss_reset_price}, short_hard_stop_loss_price: {short_hard_stop_loss_price} ({hs}), current price: {cp}, entered: {entered}".format(
            symbol=self.symbol, short_stop_loss_price = round(self.short_stop_loss_price, 3), short_stop_loss_reset_price = round(self.short_stop_loss_reset_price, 3), short_hard_stop_loss_price = round(self.short_hard_stop_loss_price, 3), hs=_HARD_STOP_LOSS_THRESHOLD, cp=cp, entered=self.price_snapshot_short_enter.price
        ))

    def _is_trade_on_new_timebucket(self):
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        return epoch_seconds // TICK_TIMEBUCKET_SECONDS - self.last_ingest_epoch_seconds // TICK_TIMEBUCKET_SECONDS > 0

    def _is_new_position_update_timebucket(self):
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        return epoch_seconds // POSITION_UPDATE_TIMEBUCKET_SECONDS - self.last_ingest_epoch_seconds // POSITION_UPDATE_TIMEBUCKET_SECONDS > 0

    def _update_last_ingest_epoch_seconds(self):
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        self.last_ingest_epoch_seconds = epoch_seconds

    def on_ingest(self):
        '''
        Decides the trading decision.
        This method is supposed to be overridden.

        :return:
        '''
        if self._is_new_position_update_timebucket():
            self.update_position_mode_on_ingest()

        self._update_last_ingest_epoch_seconds()

    def update_position_mode_on_ingest(self):
        pass

    def _make_action_on_position_mode_update(self):
        def get_traging_action():
            prev = self.prev_position_mode
            new = self.position_mode
            if prev == new:
                return TRADING_ACTION.NO_ACTION

            if new is POSITION_MODE.SHORT_ENTERED:
                return TRADING_ACTION.ENTER_SHORT

            if new is POSITION_MODE.LONG_ENTERED:
                return TRADING_ACTION.ENTER_LONG

            if new is POSITION_MODE.NO_POSITION:
                if prev is POSITION_MODE.SHORT_ENTERED:
                    return TRADING_ACTION.EXIT_SHORT
                if prev is POSITION_MODE.LONG_ENTERED:
                    return TRADING_ACTION.EXIT_LONG

            return TRADING_ACTION.NO_ACTION

        trading_action = get_traging_action()
        if trading_action is TRADING_ACTION.ENTER_LONG:
            self.enter_long_position()
        elif trading_action is TRADING_ACTION.ENTER_SHORT:
            self.enter_short_position()
        elif trading_action is TRADING_ACTION.EXIT_LONG:
            self._clear_long_position()
        elif trading_action is TRADING_ACTION.EXIT_SHORT:
            self._clear_short_position()

    def _create_price_snapshot(self):
        return None

    def _on_long_position_enter(self):
        self.in_long_position = True
        self.price_snapshot_long_enter = self._create_price_snapshot()

    def _on_short_position_enter(self):
        self.in_short_position = True
        self.price_snapshot_short_enter = self._create_price_snapshot()

    def _clear_long_position(self):
        if not self.in_long_position:
            return False
        plan = market.pick.ExitPlan(self.symbol, self._get_close_price())
        util.logging.info('long exit plan', plan)
        self.long_exit.exit(plan)
        self.in_long_position = False
        return True

    def _clear_short_position(self):
        if not self.in_short_position:
            return False
        plan = market.pick_margin.ShortExitPlan(self.symbol, self._get_close_price())
        util.logging.info('short exit plan', plan)
        self.short_exit.exit(plan)
        self.in_short_position = False
        return True

    def on_daily_trade_end(self):
        util.logging.info('clear position (if any) for symbol {symbol}'.format(symbol=self.symbol))
        self._clear_long_position()
        self._clear_short_position()
        self.long_count, self.short_count = 0, 0

    def _update_position_mode(self, position_mode):
        if self.position_mode != position_mode:
            util.logging.info('prev_position_mode: {pm}, new position_mode: {m} at {t}'.format(pm=self.prev_position_mode, m=position_mode, t=datetime.datetime.utcfromtimestamp(self.current_time.get_current_epoch_seconds()) ))
            if position_mode is POSITION_MODE.LONG_SEEKING_ENTRY:
                self.price_snapshot_long_seeking_entry = self._create_price_snapshot()
                self.min_price_seeking_long_entry = self._get_close_price()
                self.long_count += 1
                util.logging.info('long_count increased: {c}'.format(c=self.long_count))
            elif position_mode is POSITION_MODE.SHORT_SEEKING_ENTRY:
                self.price_snapshot_short_seeking_entry = self._create_price_snapshot()
                self.max_price_seeking_short_entry = self._get_close_price()
                self.short_count += 1
                util.logging.info('short_count increased: {c}'.format(c=self.short_count))
            elif position_mode is POSITION_MODE.LONG_ENTERED:
                self.highest_price_in_long_position = self._get_close_price()
                util.logging.info('reset highest_price_in_long_position: {p}'.format(p=self.highest_price_in_long_position))
            elif position_mode is POSITION_MODE.SHORT_ENTERED:
                self.lowest_price_in_short_position = self._get_close_price()
                util.logging.info('reset lowest_price_in_short_position: {p}'.format(p=self.lowest_price_in_short_position))
        self.prev_position_mode = self.position_mode
        self.position_mode = position_mode
        self._make_action_on_position_mode_update()

    def on_new_timebucket(self):
        pass

    def enter_long_position(self):
        # do not mix positions
        if self.in_long_position or self.in_short_position:
            return False
        self.in_long_position = True
        plan = market.pick.EnterPlan(self.symbol, self.positionsize, self._get_close_price())
        self.long_enter.enter(plan)
        self._on_long_position_enter()
        return True

    def enter_short_position(self):
        if self.in_long_position or self.in_short_position:
            return False
        self.in_shoft_position = True
        plan = market.pick.EnterPlan(self.symbol, self.positionsize, self._get_close_price())
        self.short_enter.enter(plan)
        self._on_short_position_enter()
        return True
