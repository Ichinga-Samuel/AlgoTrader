"""
Exit a position after a certain amount of points has been reached starting from the entry price.
"""
from logging import getLogger

from ..data_structs import OpenPosition

logger = getLogger(__name__)


async def exit_at_point(pos: OpenPosition, *, points: int = 100):
    """Exit a position after a certain amount of points have been reached starting from the entry price.
    Point is the smallest price movement of a financial instrument. in the case of forex it is one tenth of a pip i.e
    one pip is 10 points.
    """
    try:
        if not await pos.update_position():
            return
        symbol = pos.symbol
        position = pos.position
        points_reached = abs(position.price_open -position.price_current) / symbol.point
        if points_reached < points:
            return
        ok, res = await pos.close_position()
        if res and res.retcode == 10009:
            logger.error("%s:%d closed after %d", pos.symbol, pos.ticket, points)
    except Exception as err:
        logger.error("Error: %s in exit_at_points", err)
