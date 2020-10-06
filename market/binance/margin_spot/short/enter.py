import market.binance.common
import market.binance.margin.short.enter as margin_enter
import util.symbols
import util.logging

class ShortDryRun:
    def __init__(self, market_price):
        self.margin_short = margin_enter.ShortDryRun(market_price)

    def enter(self, enter_plan):
        self.margin_short.enter(enter_plan)

class Short:
    def __init__(self, market_price):
        self.margin_short = margin_enter.Short(market_price)
        self.margin_short_dry_run = margin_enter.ShortDryRun(market_price)

    def enter(self, enter_plan):
        if util.symbols.get_is_margin_binance_symbol(enter_plan.symbol):
            self.margin_short.enter(enter_plan)
        else:
            util.logging.info("symbol {symbol} is not available for margin trading, thus short forced to be dry run.".format(
                symbol=enter_plan.symbol
            ))
            self.margin_short_dry_run.enter(enter_plan)

_buy = None
def get_short(market_price, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = ShortDryRun(market_price)
    else:
        res = Short(market_price)
    _buy = res
    return res
