from market.pair.pair import Pair
import market.pick

class EnterPlan:
    def __init__(self, pair, budget, target_ratio, target_price_child, target_price_parent):
        self.pair = pair
        self.budget = budget
        self.target_ratio = target_ratio

        self.child_plan = market.pick.EnterPlan(self.pair.symbol_child, self.budget / 2.0, target_price_child)
        self.parent_plan = market.pick.EnterPlan(self.pair.symbol_parent, self.budget / 2.0, target_price_parent)

    def plan(self, market_price):
        return self.child_plan.plan(market_price), self.parent_plan.plan(market_price)

    def __str__(self):
        return 'pair: {pair}, budget: {budget}, target_ratio: {target_ratio}'.format(pair=self.pair, budget=self.budget, target_ratio=self.target_ratio)

class ExitPlan:
    def __init__(self, pair, target_ratio, target_price_child, target_price_parent):
        self.pair = pair
        self.target_ratio = target_ratio

        self.child_plan = market.pick.ExitPlan(self.pair.symbol_child, target_price_child)
        self.parent_plan = market.pick.ExitPlan(self.pair.symbol_parent, target_price_parent)

    def plan(self, market_price, holding):
        return self.child_plan.plan(market_price, holding), self.parent_plan.plan(market_price, holding)

    def __str__(self):
        return 'pair: {pair}, target_ratio: {target_ratio}'.format(pair=self.pair, target_ratio=self.target_ratio)
