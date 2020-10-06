from strategy.bar_with_times_strategy.strategy import BarWithTimesTradeStrategy

class Pair:
    def __init__(self, strategy_quote, strategy_base, target_ratio):
        self.strategy_quote = strategy_quote
        self.strategy_base = strategy_base
        self.target_ratio = target_ratio

    def set_ratio(self, ratio):
        self.ratio = ratio

    def get_current_ratio(self):
        return self.strategy_quote.aggregation.get_close_price() / self.target_ratio.aggregation.get_close_price()



