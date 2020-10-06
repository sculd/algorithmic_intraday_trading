import market.binance.common
import os, threading
import util.logging
from binance.enums import *

class ClearShortDryRun:
    def __init__(self, market_price, margin_holding):
        self.market_price = market_price
        self.margin_holding = margin_holding

    def _exit_short(self, short_exit_plan):
        symbol, price, quantity = short_exit_plan.plan(self.market_price, self.margin_holding)
        util.logging.info('(dry_run) clearing short {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = short_exit_plan.target_price, price=price))

    def _exit_short_thread(self, short_exit_plan):
        threading.Thread(target=self._exit_short, args=(short_exit_plan,)).start()

    def exit(self, short_exit_plan):
        util.logging.debug('(dry_run) shortDryRun.exit')
        self._exit_short_thread(short_exit_plan)

class ClearShort:
    def __init__(self, market_price, margin_holding):
        self.client = market.binance.common.get_client()
        self.market_price = market_price
        self.margin_holding = margin_holding
        self.lot_sizes = market.binance.common.get_lot_sizes()

    def _exit_short(self, short_exit_plan):
        symbol, price, quantity = short_exit_plan.plan(self.market_price, self.margin_holding)
        lot_size = self.lot_sizes[symbol] if symbol in self.lot_sizes else 0.001
        quantity = int(quantity / lot_size) * lot_size
        util.logging.info('clearing short {symbol}, quantity: {quantity}, target price: {target_price}, price: {price}'.format(
            symbol=symbol, quantity=quantity, target_price = short_exit_plan.target_price, price=price))

        try:
            order = self.client.create_margin_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=quantity)
            util.logging.debug('For {symbol} buy order from binance: {order}'.format(
                symbol=symbol, order=str(order)))

            coin_symbol = short_exit_plan.get_coin_symbol()
            quantity_free = self.margin_holding.get_quantity(coin_symbol)
            quantity_borrowed = self.margin_holding.get_borrowed_quantity(coin_symbol)
            quantity_repay = min(quantity_free, quantity_borrowed)
            if quantity_repay == 0:
                util.logging.debug('no amount available to repay for {coin_symbol}'.format(
                    coin_symbol=coin_symbol))
            else:
                self.client.repay_margin_loan(asset=coin_symbol, amount=quantity_repay)

            return order
        except Exception as ex:
            util.logging.error(str(ex))
            return None

    def _exit_short_thread(self, short_exit_plan):
        threading.Thread(target=self._exit_short, args=(short_exit_plan,)).start()

    def exit(self, short_exit_plan):
        '''

        :param short_exit_plan: map of symbol to quantity
        :return:
        '''
        self._exit_short_thread(short_exit_plan)


_buy = None
def get_exit_short(market_price, holding, dry_run):
    global _buy
    if _buy is not None:
        return _buy

    if dry_run:
        res = ClearShortDryRun(market_price, holding)
    else:
        res = ClearShort(market_price, holding)
    _buy = res
    return res
