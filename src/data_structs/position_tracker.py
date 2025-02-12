from typing import Callable, TypeVar
from logging import getLogger

OpenPosition = TypeVar("OpenPosition")
logger = getLogger(__name__)


class PositionTracker:
    params: dict[str, any]
    function: Callable
    number: int
    open_position: OpenPosition

    def __init__(self, function: Callable, **kwargs):
        self.function = function
        self.kwargs = kwargs
        self.number = 0

    async def __call__(self):
        try:
            await self.function(self.open_position, **self.kwargs)
        except Exception as exe:
            logger.error("%s: Error occurred in %s for %s:%d", exe, self.function.__name__,
                         self.open_position.symbol.name, self.open_position.ticket)

    def set_position(self, open_position: OpenPosition, number: int = None):
        self.open_position = open_position
        if number is not None:
            self.number = number
