import market.ally.long.enter, market.ally.long.exit
import market.ally.short.enter, market.ally.short.exit
import market.ally.holdings
import market.ally.price

def get_markets(dry_run):
    market_price = market.ally.price.Price()
    holdings = market.ally.holdings.Holdings()
    long_enter = market.ally.long.enter.get_long(market_price, dry_run)
    long_exit = market.ally.long.exit.get_exit_long(market_price, holdings, dry_run)
    short_enter = market.ally.short.enter.get_short(market_price, dry_run)
    short_exit = market.ally.short.exit.get_exit_short(market_price, holdings, dry_run)

    long_enter_dryrun = market.ally.long.enter.get_long(market_price, True)
    long_exit_dryrun = market.ally.long.exit.get_exit_long(market_price, holdings, True)
    short_enter_dryrun = market.ally.short.enter.get_short(market_price, True)
    short_exit_dryrun = market.ally.short.exit.get_exit_short(market_price, holdings, True)

    return long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun
