import argparse
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import time, datetime
from history import history
from strategy.bar_with_times_strategy.gap.run import GapTradeStrategyRun
import util.time
import config_gap
import util.logging as logging
import ingest.daily_gap.prev_day_close
import ingest.daily_gap.daily_gap


def addSecs(t, secs):
    fulldate = datetime.datetime(100, 1, 1, t.hour, t.minute, t.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()

def run(dryrun, forcerun):
    logging.set_log_name('us_equity_large_gap_trading')
    cfg = config_gap.load('config.us.gap.yaml')
    tz = config_gap.get_tz(cfg)

    prev_day_closes = ingest.daily_gap.prev_day_close.PrevDayCloses()
    trade_run = GapTradeStrategyRun(
        dryrun,
        config_gap.get_positionsize(cfg),
        prev_day_closes,
        subscription_id=os.getenv('FINANCE_STREAM_GAP_TRADING_PUBSUB_SUBSCRIPTION_ID')
    )

    cnt_loops = 0
    while True:
        cnt_loops += 1
        dt = util.time.get_utcnow().astimezone(tz)
        dt_str = str(dt.date())
        logging.info('start of the loop')

        if not forcerun and dt.weekday() >= 5:
            print('skipping the routing during weekend, weekday: {weekday} for {dt_str}'.format(
                weekday=dt.weekday(), dt_str=dt_str))
            logging.info('sleep for an hour')
            time.sleep(60 * 60)
            continue

        print('checking if run for {date_str} is already done'.format(date_str=dt_str))
        if not forcerun and history.did_run_today(cfg):
            logging.debug('run for {date_str} is already done'.format(date_str=dt_str))
            print('sleep for an hour')
            time.sleep(60 * 60)
            continue

        logging.info('run for {date_str} is not yet done'.format(date_str=dt_str))
        t_trading_start = config_gap.get_trading_start(cfg)
        logging.info('trading start time: {t}'.format(t = str(t_trading_start)))
        while True:
            t_cur = util.time.get_utcnow().astimezone(tz).time()
            seconds_to_market_open = (t_trading_start.hour - t_cur.hour) * 3600 + (t_trading_start.minute - t_cur.minute) * 60 + (t_trading_start.second - t_cur.second)
            market_just_open = True
            market_just_open = market_just_open and t_cur > t_trading_start
            market_just_open = market_just_open and t_cur < addSecs(t_trading_start, 20)

            # start updating prev close 20 min before market opens
            if abs(seconds_to_market_open) < 100:
                print('seconds_to_market_open', seconds_to_market_open)
            if forcerun or seconds_to_market_open < 1200 and seconds_to_market_open > -60:
                prev_day_closes.update()

            if forcerun or market_just_open:
                logging.info('the market open time just started'.format(dt_str=dt_str))
                history.on_run(cfg)
                trade_run.on_daily_trade_start()

                if forcerun:
                    time.sleep(5)
                    valid_gaps = ingest.daily_gap.daily_gap.daily_pick()
                    print('{l} valid gaps found {dt}'.format(l=len(valid_gaps), dt=t_cur))
                    for gap in valid_gaps:
                        trade_run.on_gap(gap)
                break

            if seconds_to_market_open > 300:
                time.sleep(60)
            else:
                time.sleep(10)

        t_close_positions = config_gap.get_close_open_positions(cfg)
        logging.info('trading start time: {t}'.format(t = str(t_trading_start)))
        while True:
            t_cur = util.time.get_utcnow().astimezone(tz).time()
            if forcerun or t_cur > t_close_positions:
                trade_run.on_daily_trade_end()
                logging.info('closing all the positions'.format(dt_str=dt_str))
                break

            time.sleep(1 * 60)

        logging.info('end of a loop')
        if forcerun:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dryrun", action="store_true", help="dryrun executes no real buy/sell trades")
    parser.add_argument("-f", "--forcerun", action="store_true", help="forces run without waiting without observing the schedule.")
    args = parser.parse_args()

    if args.forcerun:
        print('forcerun on')
    run(args.dryrun, args.forcerun)
