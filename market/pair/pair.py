
class Pair:
    def __init__(self, symbol_child, symbol_parent):
        self.symbol_child = symbol_child
        self.symbol_parent = symbol_parent

    def __str__(self):
        return 'symbol_child:{symbol_child}, symbol_parent: {symbol_parent}'.format(symbol_child=self.symbol_child, symbol_parent=self.symbol_parent)
