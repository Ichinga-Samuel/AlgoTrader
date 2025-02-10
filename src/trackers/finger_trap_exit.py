import asyncio
from logging import getLogger

from aiomql import Config, Positions, Symbol, TimeFrame, TradePosition, OrderType

logger = getLogger(__name__)


async def finger_trap_exit(*, interval: int = 60):
    config = Config()
    pos = Positions()
    print('initializing finger_trap_exit')
    while True:
        try:
            await asyncio.sleep(interval)
            # a dictionary of ticket: {timeframe, count, ema}
            tickets = config.state.get("finger_trap_exit", {})
            if not tickets:
                continue
            positions = await pos.get_positions()
            positions = [position for position in positions if position.ticket in tickets.keys()]
            await asyncio.gather(*[finger_exit(position=position, positions=pos,
                                               **tickets[position.ticket]) for position in positions])
            positions = await pos.get_positions()
            tickets = {ticket: params for ticket, params in tickets.items() if ticket in
                       [position.ticket for position in positions]}
            config.state["finger_trap_exit"] = tickets
        except Exception as err:
            logger.error("Error: %s in finger_trap_exit", err)


async def finger_exit(*, position: TradePosition, positions: Positions, timeframe: TimeFrame, count: int, ema: int):
    try:
        symbol = Symbol(name=position.symbol)
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
            await positions.close_position(position=position)
    except Exception as err:
        logger.error("Error: %s in finger_exit", err)
