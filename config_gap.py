import yaml, datetime
from pytz import timezone

def load(filename):
    with open(filename, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return cfg

def get_tz(cfg):
    return timezone(cfg['market']['timezone'])

def _get_tz_utcoffset_hours(cfg):
    tz = timezone(cfg['market']['timezone'])
    td = tz.utcoffset(datetime.datetime.utcnow())
    return td.seconds // 3600

def get_market_open(cfg):
    '''
    Get datetime.time for market open.

    :param cfg:
    :return:
    '''
    t = datetime.datetime.strptime(cfg['market']['open'], '%H:%M:%S')
    return datetime.time(t.hour, t.minute, t.second, tzinfo=get_tz(cfg))

def get_trading_start(cfg):
    '''
    Get datetime.time for market open.

    :param cfg:
    :return:
    '''
    t = datetime.datetime.strptime(cfg['market']['trading_start'], '%H:%M:%S')
    return datetime.time(t.hour, t.minute, t.second, tzinfo=get_tz(cfg))

def get_market_close(cfg):
    '''
    Get datetime.time for market close.

    :param cfg:
    :return:
    '''
    t = datetime.datetime.strptime(cfg['market']['close'], '%H:%M:%S')
    return datetime.time(t.hour, t.minute, t.second, tzinfo=get_tz(cfg))

def get_market_ingest_end(cfg):
    '''
    Get datetime.time for market close.

    :param cfg:
    :return:
    '''
    t = datetime.datetime.strptime(cfg['market']['ingest_end'], '%H:%M:%S')
    return datetime.time(t.hour, t.minute, t.second, tzinfo=get_tz(cfg))

def get_close_open_positions(cfg):
    '''
    Get datetime.time for market close.

    :param cfg:
    :return:
    '''
    t = datetime.datetime.strptime(cfg['market']['close_positions'], '%H:%M:%S')
    return datetime.time(t.hour, t.minute, t.second, tzinfo=get_tz(cfg))

def get_positionsize(cfg):
    return int(cfg['trading']['positionsize'])

