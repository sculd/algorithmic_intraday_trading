
class MockHoldings:
    def get_quantity(self, symbol):
        return 0

    def get_borrowed_quantity(self, symbol):
        return self.get_quantity(symbol)

