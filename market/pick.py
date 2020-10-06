def _get_coin_symbol(symbol):
    return symbol.replace('USDT', '')

class EnterPlan:
    def __init__(self, symbol, buy_budget, target_price):
        '''

        :param symbols: list of symbols
        :param buy_budget:
        :param target_price:
        '''
        self.buy_budget = buy_budget
        self.symbol = symbol
        self.target_price = target_price

    def get_coin_symbol(self):
        return _get_coin_symbol(self.symbol)

    def plan(self, market_price):
        symbol = self.symbol

        price = market_price.get_price(symbol)
        quantity = 0 if price == 0 else int(self.buy_budget / price)

        return (symbol, price, quantity)

    def __str__(self):
        return 'symbol:{symbol}, buy_budget: {buy_budget}, target_price: {target_price}'.format(symbol=self.symbol, buy_budget=self.buy_budget, target_price=self.target_price)

class ExitPlan:
    def __init__(self, symbol, target_price):
        '''

        :param symbols: list of symbols
        :param buy_budget:
        '''
        self.symbol = symbol
        self.target_price = target_price

    def get_coin_symbol(self):
        return _get_coin_symbol(self.symbol)

    def plan(self, market_price, holding):
        symbol = self.symbol
        price = market_price.get_price(symbol)
        quantity = holding.get_quantity(symbol)

        return (symbol, price, quantity)

    def __str__(self):
        return 'symbol:{symbol}, target_price: {target_price}'.format(symbol=self.symbol, target_price=self.target_price)
