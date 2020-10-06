import market.binance.common
import market.binance.spot.long.enter as spot_enter
import util.symbols
import util.logging

class LongDryRun:
    def __init__(self, market_price):
        self.market_price = market_price
        self.spot_long = spot_enter.LongDryRun(market_price)

    def enter(self, enter_plan):
        self.spot_long.enter(enter_plan)

class Long:
    def __init__(self, market_price):
        self.spot_long = spot_enter.Long(market_price)

    def enter(self, enter_plan):
        self.spot_long.enter(enter_plan)

_buy = None
def get_long(market_price, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = LongDryRun(market_price)
    else:
        res = Long(market_price)
    _buy = res
    return res
