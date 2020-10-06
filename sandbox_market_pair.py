import os, time

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')


import  market.tdameritrade.price, market.tdameritrade.holdings
import market.tdameritrade.long.enter, market.tdameritrade.long.exit
import market.tdameritrade.short.enter, market.tdameritrade.short.exit

import market.pair.long.enter, market.pair.long.exit
import market.pair.short.enter, market.pair.short.exit
import market.pair.pick, market.pair.pair


market_price = market.tdameritrade.price.Price()
holdings = market.tdameritrade.holdings.Holdings()
dry_run = False
long_enter = market.tdameritrade.long.enter.get_long(market_price, dry_run)
long_exit = market.tdameritrade.long.exit.get_exit_long(market_price, holdings, dry_run)
short_enter = market.tdameritrade.short.enter.get_short(market_price, dry_run)
short_exit = market.tdameritrade.short.exit.get_exit_short(market_price, holdings, dry_run)

pair = market.pair.pair.Pair('KO', 'PEP')

pair_long_enter = market.pair.long.enter.get_long(market_price, long_enter, short_enter)
enter_plan = market.pair.pick.EnterPlan(pair, 300, 0.3, 50, 130)
#pair_long_enter.enter(enter_plan)

pair_long_exit = market.pair.long.exit.get_exit_long(market_price, holdings, long_exit, short_exit)
exit_plan = market.pair.pick.ExitPlan(pair, 0.3, 50, 130)
#pair_long_exit.exit(exit_plan)


pair_short_enter = market.pair.short.enter.get_short(market_price, short_enter, long_enter)
enter_plan = market.pair.pick.EnterPlan(pair, 300, 0.3, 50, 130)
#pair_short_enter.enter(enter_plan)

pair_long_exit = market.pair.short.exit.get_exit_short(market_price, holdings, short_exit, long_exit)
exit_plan = market.pair.pick.ExitPlan(pair, 0.3, 50, 130)
#pair_long_exit.exit(exit_plan)





