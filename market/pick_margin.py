import market.pick

class ShortExitPlan(market.pick.ExitPlan):
    def __init__(self, symbol, target_price):
        '''

        :param symbols: list of symbols
        :param buy_budget:
        '''
        self.symbol = symbol
        self.target_price = target_price

    def plan(self, market_price, margin_holding):
        symbol = self.symbol
        price = market_price.get_price(symbol)
        quantity = margin_holding.get_borrowed_quantity(symbol)

        return (symbol, price, quantity)
