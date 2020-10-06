import market.tdameritrade.long.enter, market.tdameritrade.long.exit
import market.tdameritrade.short.enter, market.tdameritrade.short.exit
import market.tdameritrade.holdings
import market.tdameritrade.price

def get_markets(dry_run):
    market_price = market.tdameritrade.price.Price()
    holdings = market.tdameritrade.holdings.Holdings()
    long_enter = market.tdameritrade.long.enter.get_long(market_price, dry_run)
    long_exit = market.tdameritrade.long.exit.get_exit_long(market_price, holdings, dry_run)
    short_enter = market.tdameritrade.short.enter.get_short(market_price, dry_run)
    short_exit = market.tdameritrade.short.exit.get_exit_short(market_price, holdings, dry_run)

    long_enter_dryrun = market.tdameritrade.long.enter.get_long(market_price, True)
    long_exit_dryrun = market.tdameritrade.long.exit.get_exit_long(market_price, holdings, True)
    short_enter_dryrun = market.tdameritrade.short.enter.get_short(market_price, True)
    short_exit_dryrun = market.tdameritrade.short.exit.get_exit_short(market_price, holdings, True)

    return long_enter, long_exit, short_enter, short_exit, long_enter_dryrun, long_exit_dryrun, short_enter_dryrun, short_exit_dryrun
