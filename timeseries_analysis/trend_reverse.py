from ingest.streaming.aggregation import Aggregation, BarWithTime, Bar
import util.time
import util.logging
import util.current_time
from util.current_time import CurrentTime

from enum import Enum

class POSITION_MODE(Enum):
    NO_POSITION = 1
    SHORT = 2
    LONG = 3

class Param:
    def __init__(self, initial_change_widow_size, initial_jump_magnitude, initial_drop_magnitude, reversal_change_widow_size, reversal_drop_after_jump_magnitude, reversal_jump_after_drop_magnitude):
        '''

        :param widow_size: datetime.timedelta
        '''
        self.initial_change_widow_size = initial_change_widow_size
        self.initial_jump_magnitude = initial_jump_magnitude
        self.initial_drop_magnitude = initial_drop_magnitude
        self.reversal_change_widow_size = reversal_change_widow_size
        self.reversal_drop_after_jump_magnitude = reversal_drop_after_jump_magnitude
        self.reversal_jump_after_drop_magnitude = reversal_jump_after_drop_magnitude

class Analyze:
    def __init__(self, aggregation, param, current_time = CurrentTime()):
        self.aggregation = aggregation
        self.param = param
        self.current_time = current_time

    def analyze(self):
        epoch_seconds = self.current_time.get_current_epoch_seconds()
        cp = self.aggregation.get_close_price()
        min_price, max_price = None, None
        min_price_epoch_seconds, max_price_epoch_seconds = 0, 0

        min_drop, max_jump = None, None
        price_at_min_drop, price_at_max_jump = None, None
        min_drop_epoch_seconds, max_jump_epoch_seconds = 0, 0

        for bar_with_time in self.aggregation.bar_with_times:
            bwt_epoch_seconds = int(bar_with_time.time.timestamp())
            dt_seconds = epoch_seconds - bwt_epoch_seconds
            if dt_seconds > self.param.initial_change_widow_size.seconds:
                continue

            bwt_cp = bar_with_time.bar.close
            if min_price is None or bwt_cp < min_price:
                min_price = bwt_cp
                min_price_epoch_seconds = bwt_epoch_seconds

            if max_price is None or bwt_cp > max_price:
                max_price = bwt_cp
                max_price_epoch_seconds = bwt_epoch_seconds

            bwt_drop_change = (bwt_cp - max_price) / max_price
            bwt_jump_change = (bwt_cp - min_price) / min_price

            if min_drop is None or bwt_drop_change < min_drop:
                min_drop = bwt_drop_change
                price_at_min_drop = bwt_cp
                min_drop_epoch_seconds = bwt_epoch_seconds

            if max_jump is None or bwt_jump_change > max_jump:
                max_jump = bwt_jump_change
                price_at_max_jump = bwt_cp
                max_jump_epoch_seconds = bwt_epoch_seconds

        if price_at_min_drop is None or price_at_max_jump is None:
            return POSITION_MODE.NO_POSITION

        jump_from_min_drop = (cp - price_at_min_drop) / price_at_min_drop
        drop_from_max_jump = (cp - price_at_max_jump) / price_at_max_jump

        position_mode = POSITION_MODE.NO_POSITION

        if min_drop < self.param.initial_drop_magnitude:
            if jump_from_min_drop <= self.param.reversal_jump_after_drop_magnitude:
                util.logging.info('trend_reverse.analysis initial drop was observed, min_drop: {min_drop}, but the recovery was is not large enough: jump_from_min_drop: {jump_from_min_drop}'.format(
                        min_drop=min_drop, jump_from_min_drop=jump_from_min_drop
                    ))
            elif epoch_seconds - min_drop_epoch_seconds > self.param.reversal_change_widow_size.seconds:
                util.logging.info('trend_reverse.analysis initial drop was observed, min_drop: {min_drop}, but the recovery was too late: recovery seconds: {rs}'.format(
                        min_drop=min_drop, rs=epoch_seconds - min_drop_epoch_seconds
                    ))
            else:
                position_mode = POSITION_MODE.LONG
                util.logging.info('trend_reverse.analysis LONG position, min_drop: {min_drop}, jump_from_min_drop: {jump_from_min_drop}'.format(
                    min_drop=min_drop, jump_from_min_drop=jump_from_min_drop
                ))
        elif max_jump > self.param.initial_jump_magnitude and drop_from_max_jump < self.param.reversal_drop_after_jump_magnitude and epoch_seconds - max_jump_epoch_seconds <= self.param.reversal_change_widow_size.seconds:
            if drop_from_max_jump >= self.param.reversal_drop_after_jump_magnitude:
                util.logging.info('trend_reverse.analysis initial jump was observed. max_jump: {max_jump}, but the recovery was is not large enough: drop_from_max_jump: {drop_from_max_jump}'.format(
                    max_jump=max_jump, drop_from_max_jump=drop_from_max_jump
                ))
            elif epoch_seconds - max_jump_epoch_seconds > self.param.reversal_change_widow_size.seconds:
                util.logging.info('trend_reverse.analysis initial jump was observed. max_jump: {max_jump}, but the recovery was too late: recovery seconds: {rs}'.format(
                    max_jump=max_jump, rs=epoch_seconds - min_drop_epoch_seconds
                ))
            else:
                position_mode = POSITION_MODE.SHORT
                util.logging.info('trend_reverse.analysis SHORT position. max_jump: {max_jump}, drop_from_max_jump: {drop_from_max_jump}'.format(
                    max_jump=max_jump, drop_from_max_jump=drop_from_max_jump
                ))

        return position_mode




