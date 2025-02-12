import asyncio
from logging import getLogger

from aiomql import Config, backtest_sleep, Positions

logger = getLogger(__name__)


async def tracker(*, interval: int = 5):
    config = Config()
    poss = Positions()
    while True:
        try:
            sleep = asyncio.sleep if config.mode == "live" else backtest_sleep
            await sleep(interval)
            tracked_positions = config.state.get("tracked_positions", {})
            await asyncio.gather(*(pos.track() for pos in tracked_positions.values()))
            all_pos = await poss.get_positions()
            all_pos = {pos.ticket for pos in all_pos}
            config.state["tracked_positions"] = {pos.ticket: pos for pos in tracked_positions.values() if pos.ticket in all_pos}
        except Exception as exe:
            logger.error("%s: Error occurred in main position tracker", exe)