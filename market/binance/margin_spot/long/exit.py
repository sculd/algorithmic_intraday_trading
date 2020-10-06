import market.binance.common
import market.binance.spot.long.exit as spot_exit
import util.logging
from binance.enums import *

class ExitLongDryRun:
    def __init__(self, market_price, holding):
        self.spot_exit = spot_exit.ExitLongDryRun(market_price, holding)

    def exit(self, exit_plan):
        self.spot_exit.exit(exit_plan)

class ExitLong:
    def __init__(self, market_price, holding):
        self.spot_exit = spot_exit.ExitLong(market_price, holding)

    def exit(self, exit_plan):
        self.spot_exit.exit(exit_plan)

_buy = None
def get_exit_long(market_price, holding, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = ExitLongDryRun(market_price, holding)
    else:
        res = ExitLong(market_price, holding)
    _buy = res
    return res
