import config
import util.time as util_time

_run_dates = set()


def _did_run_today_run_dates(cfg):
    tz = config.get_tz(cfg)
    dt_str = str(util_time.get_utcnow().astimezone(tz).date())
    if dt_str in _run_dates:
        return True
    return False

def did_run_today(cfg):
    '''
    Tells if download already happened for today.

    :return: boolean
    '''
    return _did_run_today_run_dates(cfg)

def on_run(cfg):
    global _run_dates
    _run_dates.add(util_time.get_today_str_tz(cfg))
