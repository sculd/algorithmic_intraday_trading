import market.tradier.history
import market.tradier.price
import util.symbols
import publish.pubsub
import time, concurrent
from concurrent.futures import ThreadPoolExecutor

_h = market.tradier.history.History()
_p = market.tradier.price.Price()

class Gap:
    def __init__(self, symbol, gap):
        self.symbol = symbol
        self.gap = gap

        self.threshold = 0.02
        for i in range(3, 11):
            if abs(gap) >= 0.01 * i:
                self.threshold = 0.01 * i
        if gap < 0:
            self.threshold *= -1

def _get_gap(symbol, days_delta=0):
    prev_close = _h.get_prev_day_close(symbol, days_delta=days_delta+1)
    cur_quote = _h.get_prev_day_open(symbol, days_delta=days_delta)

    if prev_close == 0:
        return 0.0
    gap = 1.0 * (cur_quote - prev_close) / prev_close
    if gap == -1:
        print('error, cur_quote is zero')
    return gap

def _record_gap(symbol, gaps, i, days_delta):
    gap = _get_gap(symbol, days_delta=days_delta)
    gaps[i] = gap

def _daily_picks_among_symbols(symbols, days_delta=0):
    '''
    Return those with the gap larger than 2%.

    :param symbols:
    :return: list
    '''

    #symbols = symbols[:50]

    res = []
    batch_size = 50
    with ThreadPoolExecutor(max_workers=50) as executor:
        gaps = [0 for _ in range(len(symbols))]
        futures = []

        batch_i = 0
        while True:
            i_head = batch_size * batch_i
            batch = symbols[i_head : batch_size * (batch_i + 1)]
            futures += [executor.submit(_record_gap, symbol, gaps, i_head + i, days_delta) for i, symbol in enumerate(batch)]
            batch_i += 1
            if batch_size * batch_i >= len(symbols):
                break
            time.sleep(5)

        print('made all the requests')
        for future in futures:
            future.result()

    print('##### all futures returned #####')
    for i, gap in enumerate(gaps):
        symbol = symbols[i]
        gap = gaps[i]
        print(i, symbol, gap)
        if abs(gap) > 0.20:
            continue
        print('a gap for {symbol} {g}%'.format(symbol=symbol, g=round(gap * 100, 3)))
        if abs(gap) < 0.05:
            continue

        print('found a valid gap for {symbol}'.format(symbol=symbol))
        res.append(
            Gap(symbol, gap)
        )
    return res

def daily_pick(days_delta=0):
    symbols = util.symbols.get_symbols_snp500()
    return _daily_picks_among_symbols(symbols, days_delta=days_delta)

def pick_and_publish(topic_id, days_delta=0):
    picks = daily_pick(days_delta=days_delta)
    for pick in picks:
        js = {
            'symbol': pick.symbol,
            'change': pick.gap,
            'threshold': pick.threshold
        }
        publish.pubsub.publish(topic_id, js)

