import market.tradier.long.enter, market.tradier.long.exit
import market.tradier.short.enter, market.tradier.short.exit
import market.tradier.holdings
import market.tradier.price

def get_markets(dry_run):
    market_price = market.tradier.price.Price()
    holdings = market.tradier.holdings.Holdings()
    long_enter = market.tradier.long.enter.get_long(market_price, dry_run)
    long_exit = market.tradier.long.exit.get_exit_long(market_price, holdings, dry_run)
    short_enter = market.tradier.short.enter.get_short(market_price, dry_run)
    short_exit = market.tradier.short.exit.get_exit_short(market_price, holdings, dry_run)

    long_enter_dryrun = market.tradier.long.enter.get_long(market_price, True)
    long_exit_dryrun = market.tradier.long.exit.get_exit_long(market_price, holdings, True)
    short_enter_dryrun = market.tradier.short.enter.get_short(market_price, True)
    short_exit_dryrun = market.tradier.short.exit.get_exit_short(market_price, holdings, True)

    return long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun
