from enum import Enum
import util.logging
from market.util import EQUITY_BROKER_MODE
import market.util
import market.pair.long.enter, market.pair.long.exit
import market.pair.short.enter, market.pair.short.exit

def get_equity_broker_mode_from_str(broker_str):
    if broker_str == 'ally':
        return EQUITY_BROKER_MODE.ALLY
    elif broker_str == 'tradier':
        return EQUITY_BROKER_MODE.TRADIER
    elif broker_str == 'tdameritrade':
        return EQUITY_BROKER_MODE.TDAMERITRADE

    util.logging.warning("broker param {b} is not valid thus falling to default tdameritrade".format(b=broker_str))
    return EQUITY_BROKER_MODE.TDAMERITRADE

def get_markets(equity_broker_mode, dry_run):
    long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun = market.util.get_markets(equity_broker_mode, dry_run)
    market_price = market.util.get_market_price(equity_broker_mode)
    holdings = market.util.get_holdings(equity_broker_mode)

    pair_long_enter = market.pair.long.enter.get_long(market_price, long_enter, short_enter)
    pair_long_exit = market.pair.long.exit.get_exit_long(market_price, holdings, long_exit, short_exit)
    pair_short_enter = market.pair.short.enter.get_short(market_price, short_enter, long_enter)
    pair_short_exit = market.pair.short.exit.get_exit_short(market_price, holdings, short_exit, long_exit)

    return pair_long_enter, pair_long_exit, pair_short_enter, pair_short_exit
