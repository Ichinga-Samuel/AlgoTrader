from logging import getLogger

from aiomql import  TimeFrame, OrderType

from ..data_structs import OpenPosition

logger = getLogger(__name__)


async def finger_exit(pos: OpenPosition, *, timeframe: TimeFrame, count: int, ema: int):
    try:
        if not await pos.update_position():
            return
        symbol = pos.symbol
        position = pos.position
        candles = await symbol.copy_rates_from_pos(timeframe=timeframe, count=count)
        candles.ta.ema(length=ema, append=True)
        candles.rename(**{f"EMA_{ema}": "ema"})
        close = False
        if position.type == OrderType.BUY:
            # close below ema
            cbe = candles.ta_lib.below(candles.close, candles.ema)
            if cbe.iloc[-1]:
                close = True
        elif position.type == OrderType.SELL:
            # close above ema
            cae = candles.ta_lib.above(candles.close, candles.ema)
            if cae.iloc[-1]:
                close = True
        if close:
            await pos.close_position()
    except Exception as err:
        logger.error("Error: %s in finger_exit", err)
