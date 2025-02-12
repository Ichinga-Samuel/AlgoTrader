from logging import getLogger
from aiomql import TimeFrame, OrderType

from ..data_structs import OpenPosition

logger = getLogger(__name__)


async def atr_trailer(pos: OpenPosition, *, timeframe: TimeFrame = TimeFrame.D1,
                      period: int = 22, multiplier: float = 3, cc: int = 500):
    try:
        if not await pos.update_position():
            return
        sym = pos.symbol
        position = pos.position
        candles = await sym.copy_rates_from_pos(timeframe=timeframe, count=cc)
        candles.ta.atr(length=period, append=True)
        candles.rename(inplace=True, **{f'ATRr_{period}': 'atr'})
        change = False
        new_sl = position.sl
        current_candle = candles[-1]
        if OrderType(position.type) == OrderType.BUY:
            new_sl = max(candles[-22:].high) - (current_candle.atr * multiplier)
            change = max(new_sl, position.sl)  # only change the sl if the new_sl is greater than the previous sl
        elif OrderType(position.type) == OrderType.SELL:
            new_sl = min(candles[-22:].low) + (current_candle.atr * multiplier)
            change = min(new_sl, position.sl) # only change the sl if the new_sl is less than the previous sl
        if change:
            ok, res = await pos.modify_stops(sl=new_sl)
            if ok:
                logger.info("Stops modified successfully for %s:%d in atr_trailer", pos.symbol, pos.ticket)
            else:
                logger.warning("Unable to modify order %s:%d in atr_trailer", pos.symbol, pos.ticket)
    except Exception as exe:
        logger.error("%d: Error occurred in atr_trailer", exe)
