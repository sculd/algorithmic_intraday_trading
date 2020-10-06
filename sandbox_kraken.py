import market.binance.common
from binance.client import Client
import time, pprint

client = market.binance.common.get_client()

'''
exinfo = client.get_exchange_info()
symbols_usdt = [s for s in exinfo['symbols']]
symbols_usdt = [s for s in symbols_usdt if s['symbol'].endswith('USDT')]
symbols_usdt = [s['symbol'] for s in symbols_usdt if s['status'] == 'TRADING']
pprint.pprint(symbols_usdt)
#'''

'''
now_epoch_milli = int(time.time()) * 1000
klines = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_15MINUTE, startTime = now_epoch_milli - 3600 * 1000)
pprint.pprint(klines)
#'''

import market.binance.price
bp = market.binance.price.Price()
pprint.pprint(bp.get_price('BTCUSDT'))


'''
trades = client.get_recent_trades(symbol='LTCUSDT')
pprint.pprint(trades)
#'''

'''
import market.binance.price
binance_price = market.binance.price.Price()
pprint.pprint(binance_price.get_price('LTCUSDT'))
'''

'''
import market.binance.holdings
binance_holding = market.binance.holdings.Holdings()
pprint.pprint(binance_holding.get())
'''

'''
agg_trades = client.aggregate_trade_iter(symbol='LTCUSDT', start_str='2 minutes ago UTC')
# iterate over the trade iterator
for trade in agg_trades:
    pprint.pprint(trade)
#'''

#'''
from binance.enums import *
order = client.order_market_buy(symbol='LTCUSDT', quantity=1)

'''
order = client.create_test_order(
    symbol='LTCUSDT',
    side=SIDE_BUY,
    type=ORDER_TYPE_MARKET,
    quantity=1)
'''

pprint.pprint(order)
#'''
