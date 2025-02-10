import asyncio
from logging import getLogger
from aiomql import Config, Positions

logger = getLogger(__name__)


async def exit_at_profit(*, interval: float = 10):
    """Exit a position after a certain amount of profit has been reached starting from the entry price.

    Args:
        interval (float): The interval in seconds to check the positions. defaults to 10.
    """
    config = Config()
    pos = Positions()
    print('initializing exit_at_profit')
    while True:
        try:
            # at each iteration, get the positions and check if the profit has been reached
            # get the tickets of the positions to be tracked by this tracker
            await asyncio.sleep(interval)  # sleep at each iteration

            # tickets are dictionary of ticket: profit
            tickets = config.state.get("exit_at_profit", {})

            # if there are no tickets, continue
            if not tickets:
                continue

            # get the positions
            positions = await pos.get_positions()

            # get the positions that are being tracked and have reached their exit profit
            positions_to_close = [position for position in positions if position.ticket in tickets.keys() and
                                  position.profit > tickets[position.ticket]]
            # close the positions
            if positions_to_close:
                pos.positions = positions_to_close
                res = await pos.close_all()
                logger.info("Closed positions: %s", res)

            # update the positions
            positions = await pos.get_positions()
            tickets = {ticket: profit for ticket, profit in tickets.items() if
                       ticket in [position.ticket for position in positions]}
            config.state["exit_at_profit"] = tickets
        except Exception as err:
            logger.error("Error: %s in exit_at_profit", err)
            continue
