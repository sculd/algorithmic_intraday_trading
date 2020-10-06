
import util.logging

class MockHoldings:
    def __init__(self):
        pass

    def get(self):
        return {}

    def get_quantity(self, symbol):
        return 0

    def get_borrowed_quantity(self, symbol):
        return self.get_quantity(symbol)
