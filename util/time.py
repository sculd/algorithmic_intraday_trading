import datetime
import pytz
import config

def get_utcnow():
    tz_utc = pytz.utc
    return tz_utc.localize(datetime.datetime.utcnow())

def get_now_tz(cfg):
    tz = config.get_tz(cfg)
    return get_utcnow().astimezone(tz)

def get_now_time_tz(cfg):
    '''
    get datetime.time of now in korean time zone.
    :return:
    '''
    tz = config.get_tz(cfg)
    now_tz = get_utcnow().astimezone(tz)
    return datetime.time(now_tz.hour, now_tz.minute, now_tz.second, tzinfo=tz)

def get_today_tz(cfg):
    '''
    :return: e.g: 2019-12-25
    '''
    tz = config.get_tz(cfg)
    return get_utcnow().astimezone(tz).date()

def get_today_str_tz(cfg):
    '''
    :return: e.g: 2019-12-25
    '''
    return str(get_today_tz(cfg))

def get_today_v_tz(cfg):
    '''
    :return: e.g: 2019-12-25
    '''
    tz = config.get_tz(cfg)
    return get_utcnow().astimezone(tz).strftime('%Y%m%d')

def time_diff_seconds(t1, t2):
    '''
    Get datetime.timedelta between two datetime.time

    :param t1:
    :param t2:
    :return:
    '''
    today = datetime.date.today()
    dt1, dt2 = datetime.datetime.combine(today, t1), datetime.datetime.combine(today, t2)
    tf = dt1 - dt2
    return tf.days * 24 * 3600 + tf.seconds

def truncate_utc_timestamp_to_minute(timestamp_seconds):
    t = datetime.datetime.utcfromtimestamp(timestamp_seconds)
    t_tz = pytz.utc.localize(t)
    t_tz_minute = t_tz.replace(second=0, microsecond=0)
    return t_tz_minute

def epoch_seconds_to_str(timestamp_seconds):
    t = datetime.datetime.utcfromtimestamp(timestamp_seconds)
    t_tz = pytz.utc.localize(t)
    return str(t_tz)