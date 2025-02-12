from logging import getLogger

from ..data_structs import OpenPosition

logger = getLogger(__name__)


async def exit_at_profit(pos: OpenPosition, *, profit: float=5):
    """Exit a position after a certain amount of profit has been reached starting from the entry price.
    """
    try:
        if not await pos.update_position():
            return
        if pos.position.profit >= profit:
            ok, res = pos.close_position()
            if ok:
                logger.info("%s:%d closed at %d", pos.symbol, pos.ticket, profit)
            else:
                logger.warning("Unable to close position with exit_at_profit", pos.symbol, pos.ticket)
    except Exception as err:
        logger.error("Error: %s in exit_at_profit", err)
