import argparse
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import time
from history import history
import util.time
import config_boxrange
import util.logging as logging
import strategy.ingestion_run.bar_with_times_ingestion_run.polygon_ingestion_run
from strategy.bar_with_times_strategy.box_range.exit_momentum.equity.run import BoxRangeExitMomentumTradeStrategyRun
from strategy.orderbook_strategy.orderbook_flow.run import get_equity_broker_mode_from_str


def run(dryrun, forcerun, broker_str):
    logging.set_log_name('us_equity_rawadata_trading')
    if broker_str == 'tradier':
        logging.set_log_name('us_intraday_trading_tradier')
    cfg = config_boxrange.load('config.us.boxrange.yaml')
    tz = config_boxrange.get_tz(cfg)
    logging.info("reading pubsub from {id}".format(id=os.getenv('FINANCE_STREAM_RAWDATA_TRADING_PUBSUB_SUBSCRIPTION_ID')))

    trade_run = BoxRangeExitMomentumTradeStrategyRun(
        dryrun,
        config_boxrange.get_positionsize(cfg),
        subscription_id = os.getenv('FINANCE_STREAM_RAWDATA_TRADING_PUBSUB_SUBSCRIPTION_ID'),
        equity_broker_mode = get_equity_broker_mode_from_str(broker_str)
    )

    cnt_loops = 0
    while True:
        cnt_loops += 1
        dt = util.time.get_utcnow().astimezone(tz)
        dt_str = str(dt.date())
        print('start of the loop')

        if dt.weekday() >= 5:
            logging.info('skipping the routing during weekend, weekday: {weekday} for {dt_str}'.format(
                weekday=dt.weekday(), dt_str=dt_str))
            print('sleep for an hour')
            time.sleep(60 * 60)
            continue

        logging.debug('checking if run for {date_str} is already done'.format(date_str=dt_str))
        if not forcerun and history.did_run_today(cfg):
            logging.debug('run for {date_str} is already done'.format(date_str=dt_str))
            print('sleep for 10 minutes')
            time.sleep(10 * 60)
            continue

        t_trading_start = config_boxrange.get_trading_start(cfg)
        print('trading start time: {t}'.format(t = str(t_trading_start)))
        while True:
            t_cur = util.time.get_utcnow().astimezone(tz).time()
            logging.debug('checking if the schedule time for trading start for {dt_str} has reached'.format(dt_str=dt_str))
            if forcerun or t_cur > t_trading_start:
                trade_run.on_daily_trade_start()
                break

            logging.debug('schedule time for market open for {t_run_after} not yet reached at {t_cur}'.format(t_run_after=t_trading_start, t_cur=t_cur))
            time.sleep(10 * 60)

        if forcerun:
            print('in forcerun mode, running for 70 seconds')
            time.sleep(70)

        t_ingest_end = config_boxrange.get_market_ingest_end(cfg)
        while True:
            t_cur = util.time.get_utcnow().astimezone(tz).time()
            logging.debug('checking if the schedule time for ingestion end for {dt_str} has reached'.format(dt_str=dt_str))
            # disable as it is too noisy
            # logging.info(trade_run.get_status_string())
            if forcerun or t_cur > t_ingest_end:
                trade_run.on_daily_trade_end()
                history.on_run(cfg)
                break

            logging.debug('schedule time to end ingestion for {t_run_after} not yet reached at {t_cur}'.format(t_run_after=t_ingest_end, t_cur=t_cur))
            time.sleep(60 * 10)

        print('end of a loop')
        if forcerun:
            # forcerun runs only once
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dryrun", action="store_true", help="dryrun executes no real buy/sell trades")
    parser.add_argument("-f", "--forcerun", action="store_true", help="forces run without waiting without observing the schedule.")
    parser.add_argument("-b", "--broker", type=str, choices=["ally", "tradier", "tdameritrade"], help="broker to trade in.")
    args = parser.parse_args()

    if args.forcerun:
        print('forcerun on')
    run(args.dryrun, args.forcerun, args.broker)
