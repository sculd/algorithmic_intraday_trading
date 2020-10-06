import market.binance.common
import time, pprint

import market.binance.spot.long.enter, market.binance.spot.long.exit
import market.binance.margin.long.enter, market.binance.margin.long.exit
import market.binance.margin.short.enter, market.binance.margin.short.exit
import market.pick
import market.binance.holdings
import market.binance.margin.holdings
import market.pick_margin
import market.binance.price

import market.pick
import time
import util.logging

util.logging.log_to_std = True

market_price = market.binance.price.Price()
margin_holdings = market.binance.margin.holdings.MarginHoldings()
holdings = market.binance.holdings.Holdings()

long_enter = market.binance.spot.long.enter.get_long(market_price, False)
long_exit = market.binance.spot.long.exit.get_exit_long(market_price, holdings, False)
long_margin_enter = market.binance.margin.long.enter.get_long(market_price, False)
long_margin_exit = market.binance.margin.long.exit.get_exit_long(market_price, margin_holdings, False)


symbol = 'XTZUSDT'

#long_exit.exit(market.pick.ExitPlan('ATOMUSDT', 10.0))
#long_exit.exit(market.pick.ExitPlan('KAVAUSDT', 10.0))
#long_exit.exit(market.pick.ExitPlan('XTZUSDT', 10.0))
#long_exit.exit(market.pick.ExitPlan('BANDSUSDT', 10.0))

#holdings._print_account_info()
#margin_holdings._print_account_info()

'''
long_enter.enter(market.pick.EnterPlan(symbol, 50, 2.8))
time.sleep(5)
#'''

#print(margin_holdings.get_quantity(symbol))

'''
long_exit.exit(market.pick.ExitPlan(symbol, 2.8))
time.sleep(5)

print(margin_holdings.get_quantity(symbol))
#'''

'''
short_enter = market.binance.margin.short.enter.get_short(market_price, False)
short_exit = market.binance.margin.short.exit.get_exit_short(market_price, holdings, False)

symbol_short = 'BANDUSDT'

short_enter.enter(market.pick.EnterPlan(symbol_short, 50, 2.0))
time.sleep(5)

print(margin_holdings.get_quantity(symbol))

short_exit.exit(market.pick_margin.ShortExitPlan(symbol_short, 2.0))
time.sleep(5)
'''


from binance.client import Client
client = market.binance.common.get_client()

exinfo = client.get_exchange_info()
#print(exinfo)

#pprint.pprint(client.get_all_orders(symbol=symbol))

def get_symbols_usdt():
    exinfo = client.get_exchange_info()
    symbols_usdt = [s for s in exinfo['symbols']]
    symbols_usdt = [s for s in symbols_usdt if s['symbol'].endswith('USDT')]
    symbols_usdt = [s['symbol'] for s in symbols_usdt if s['status'] == 'TRADING']
    return symbols_usdt

def get_symbols_margin_usdt():
    exinfo = client.get_exchange_info()
    symbols_usdt = [s for s in exinfo['symbols']]
    symbols_usdt = [s for s in symbols_usdt if s['symbol'].endswith('USDT')]
    symbols_usdt = [s for s in symbols_usdt if s['isMarginTradingAllowed']]
    symbols_usdt = [s['symbol'] for s in symbols_usdt if s['status'] == 'TRADING']
    return symbols_usdt

