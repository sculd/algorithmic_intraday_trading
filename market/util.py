from enum import Enum
import util.logging
import market.tdameritrade.util
import market.ally.util
import market.tradier.util
import market.tdameritrade.price
import market.ally.price
import market.tradier.price
import market.tdameritrade.holdings
import market.ally.holdings
import market.tradier.holdings


class EQUITY_BROKER_MODE(Enum):
    ALLY = 1
    TRADIER = 2
    TDAMERITRADE = 3

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
    if equity_broker_mode is EQUITY_BROKER_MODE.TDAMERITRADE:
        long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun = market.tdameritrade.util.get_markets(dry_run)
    elif equity_broker_mode is EQUITY_BROKER_MODE.ALLY:
        long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun = market.ally.util.get_markets(dry_run)
    elif equity_broker_mode is EQUITY_BROKER_MODE.TRADIER:
        long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun = market.tradier.util.get_markets(dry_run)
    else:
        long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun = market.tdameritrade.util.get_markets(dry_run)

    return long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun

def get_market_price(equity_broker_mode):
    if equity_broker_mode is EQUITY_BROKER_MODE.TDAMERITRADE:
        market_price = market.tdameritrade.price.Price()
    elif equity_broker_mode is EQUITY_BROKER_MODE.ALLY:
        market_price = market.ally.price.Price()
    elif equity_broker_mode is EQUITY_BROKER_MODE.TRADIER:
        market_price = market.tradier.price.Price()
    else:
        market_price = market.tdameritrade.price.Price()

    return market_price

def get_holdings(equity_broker_mode):
    if equity_broker_mode is EQUITY_BROKER_MODE.TDAMERITRADE:
        holdings = market.tdameritrade.holdings.Holdings()
    elif equity_broker_mode is EQUITY_BROKER_MODE.ALLY:
        holdings = market.ally.holdings.Holdings()
    elif equity_broker_mode is EQUITY_BROKER_MODE.TRADIER:
        holdings = market.tradier.holdings.Holdings()
    else:
        holdings = market.tdameritrade.holdings.Holdings()

    return holdings
