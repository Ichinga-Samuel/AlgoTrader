from aiomql import Candles, Candle


def swing_low(candles: Candles, n=1, key='low') -> Candle | None:
    """Given a candles object, find the most recent swing low using a five candles setup."""
    c = 0
    # iterate through the candles in reverse, starting from the third candle
    for index, candle in enumerate(reversed(candles)):
        if index < 2:
            continue

        # find the two candles by the left and right of the current candle
        fl, sl = candles[candle.Index - 2], candles[candle.Index - 1]
        fr, sr = candles[candle.Index + 1], candles[candle.Index + 2]
        if fl[key] > sl[key] > candle[key] < fr[key] < sr[key]:
            c += 1
            if c == n:
                return candle
            continue


def swing_high(candles: Candles, n=1, key='high') -> Candle | None:
    """Given a candles object, find the most recent swing high using a five candles setup."""
    c = 0
    for index, candle in enumerate(reversed(candles)):
        if index < 2:
            continue
        # find the two candles by the left and right of the current candle
        fl, sl = candles[candle.Index - 2], candles[candle.Index - 1]
        fr, sr = candles[candle.Index + 1], candles[candle.Index + 2]
        if fl[key] < sl[key] < candle[key] > fr[key] > sr[key]:
            c += 1
            if c == n:
                return candle
            continue
