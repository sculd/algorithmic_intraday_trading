_FILENAME_NASDAQ = 'symbols/nasdaq.txt'
_FILENAME_SNP100 = 'symbols/snp100.txt'
_FILENAME_SNP500 = 'symbols/snp500.txt'
_FILENAME_QUANDL = 'symbols/symbols.quandl.txt'
_FILENAME_BINANCE = 'symbols/binance.txt'
_FILENAME_BINANCE_MARGIN = 'symbols/binance.margin.txt'
_FILENAME_AIRLINE = 'symbols/airline_symbols.txt'
_FILENAME_HOTEL_RESORT = 'symbols/hotel_resort_symbols.txt'
_FILENAME_OIL_GAS = 'symbols/oil_gas_symbols.txt'
_FILENAME_RESTAURANT = 'restaurant_symbols/airline_symbols.txt'

def _load_symbols_from_file(filename):
    symbols = []
    for symbol in open(filename, 'r'):
        symbol = symbol.strip()
        symbols.append(symbol)
    return symbols


def get_symbols_nasdaq():
    return _load_symbols_from_file(_FILENAME_NASDAQ)

def get_symbols_snp100():
    return _load_symbols_from_file(_FILENAME_SNP100)

def get_symbols_snp500():
    return _load_symbols_from_file(_FILENAME_SNP500)

def get_symbols_quandl():
    return _load_symbols_from_file(_FILENAME_QUANDL)

def get_symbols_binance():
    return _load_symbols_from_file(_FILENAME_BINANCE)

def get_symbols_margin_binance():
    return _load_symbols_from_file(_FILENAME_BINANCE_MARGIN)

def get_symbols_airline():
    return _load_symbols_from_file(_FILENAME_AIRLINE)

def get_symbols_hotel_resort():
    return _load_symbols_from_file(_FILENAME_HOTEL_RESORT)

def get_symbols_oil_gas():
    return _load_symbols_from_file(_FILENAME_OIL_GAS)

def get_symbols_restaurant():
    return _load_symbols_from_file(_FILENAME_RESTAURANT)

_symbols_margin_binance = None
def get_is_margin_binance_symbol(symbol):
    global _symbols_margin_binance
    if _symbols_margin_binance is None:
        _symbols_margin_binance = set(get_symbols_margin_binance())
    return symbol in _symbols_margin_binance


