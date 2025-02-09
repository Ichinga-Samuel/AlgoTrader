"""
Exit a position after a certain amount of points has been reached starting from the entry price.
"""
import asyncio
from logging import getLogger
import random

from aiomql import Config, Positions, Symbol

logger = getLogger(__name__)


async def exit_at_point(*, interval: int = 10):
    """Exit a position after a certain amount of points have been reached starting from the entry price.
    Point is the smallest price movement of a financial instrument. in the case of forex it is one tenth of a pip i.e
    one pip is 10 points.

    Args:
        points (int): The amount of points to wait for. defaults to 0.
        interval (int): The interval in seconds to check the positions. defaults to 10.
    """
    config = Config()
    pos = Positions()
    print('initializing exit_at_point')
    while True:
        try:
            # at each iteration, get the positions and check if the points have been reached
            # get the tickets of the positions to be tracked by this tracker
            print('inside while loop of exit_at_point', random.random())
            await asyncio.sleep(interval)  # sleep at each iteration

            # tickets are dictionary of ticket: points
            tickets = config.state.get("exit_at_point", {})

            # if there are no tickets, continue
            if not tickets:
                continue

            # get the positions
            positions = await pos.get_positions()
            # get the positions that are being tracked
            tracked_positions = [position for position in positions if position.ticket in tickets.keys()]

            # exit the positions that have reached the points
            for position in tracked_positions:
                symbol = Symbol(name=position.symbol)
                await symbol.initialize()
                points_reached = abs(position.price_open - symbol.tick.ask) / symbol.point
                if points_reached >= tickets[position.ticket]:
                    res = await pos.close_position(position=position)
                    if res and res.retcode == 10009:
                        tickets.pop(position.ticket, None)

            # update the tickets
            config.state["exit_after_points"] = tickets
        except Exception as err:
            logger.error("Error: %s in exit_at_points", err)
            continue
