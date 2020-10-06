import market.binance.common
import market.binance.margin.short.exit as margin_exit
import os, threading
import util.logging
from binance.enums import *

class ClearShortDryRun:
    def __init__(self, market_price, margin_holding):
        self.margin_exit = margin_exit.ClearShortDryRun(market_price, margin_holding)

    def exit(self, short_exit_plan):
        self.margin_exit.exit(short_exit_plan)

class ClearShort:
    def __init__(self, market_price, margin_holding):
        self.margin_exit = margin_exit.ClearShort(market_price, margin_holding)

    def exit(self, short_exit_plan):
        self.margin_exit.exit(short_exit_plan)

_buy = None
def get_exit_short(market_price, holding_margin, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = ClearShortDryRun(market_price, holding_margin)
    else:
        res = ClearShort(market_price, holding_margin)
    _buy = res
    return res
