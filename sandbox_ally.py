import market.ally.long.enter
import market.ally.long.exit
import market.ally.price
import market.ally.holdings
import market.pick
import time
import util.logging

util.logging.log_to_std = True

market_price = market.ally.price.Price()
holdings = market.ally.holdings.Holdings()

long_enter = market.ally.long.enter.get_long(market_price, False)
long_exit = market.ally.long.exit.get_exit_long(market_price, holdings, False)

symbol = 'PCOM'

long_enter.enter(market.pick.EnterPlan(symbol, 50, 10.0))
time.sleep(5)

'''
print(holdings.get_quantity(symbol))

long_exit.exit(market.pick.ExitPlan(symbol, 10.0))
time.sleep(5)
'''
print(holdings.get_quantity(symbol))


