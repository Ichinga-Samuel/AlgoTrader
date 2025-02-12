from dataclasses import dataclass, field
from typing import Union
from logging import getLogger

from aiomql import (Symbol, TradePosition, Order, TradeAction, OrderSendResult, OrderType, Positions, Config)

from .position_tracker import PositionTracker

logger = getLogger()


@dataclass
class OpenPosition:
    symbol: Symbol
    ticket: int
    position: TradePosition
    is_open: bool = True
    trackers: list[PositionTracker] = field(default_factory=list)
    is_hedged: bool = False
    hedged_position: Union['OpenPosition', None] = None  # the hedge of the position
    position_hedged: Union['OpenPosition', None] = None  # the position that is hedged
    positions: Positions = field(default_factory=Positions)
    config: Config = field(default=Config)
    state_key: str = 'tracked_positions'

    def add_tracker(self, *, tracker: PositionTracker, number: int = None):
        number = number or len(self.trackers)
        tracker.set_position(self, number)
        self.trackers.append(tracker)
        self.trackers.sort(key=lambda x: x.number)

    async def update_position(self) -> bool:
        pos = await self.positions.get_position_by_ticket(ticket=self.ticket)
        if pos is not None:
            self.position = pos
            self.is_open = True
            return self.is_open
        self.is_open = False
        return self.is_open

    async def modify_stops(self, *, sl: float = None, tp: float = None,) -> tuple[bool, OrderSendResult | None]:
        try:
            sl = sl if sl is not None else self.position.sl
            tp = tp if tp is not None else self.position.tp

            order = Order(position=self.ticket, sl=sl, tp=tp, action=TradeAction.SLTP)
            res = await order.send()
            if res and res.retcode == 10009:
                await self.update_position()
                return True, res
            else:
                return False, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.modify_stops for %s:%d",
                         exe, self.__class__.__name__, self.symbol.name, self.ticket)
            return False, None

    def remove_from_state(self):
        self.config.state.get(self.state_key, {}).pop(self.ticket, None)

    async def close_position(self) -> tuple[bool, OrderSendResult | None]:
        try:
            res = await self.positions.close_position(position=self.position)
            if res.retcode == 10009:
                self.is_open = False
                self.remove_from_state()
                return True, res
            else:
                return False, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.close_position for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)
            return False, None

    async def track(self):
        try:
            for tracker in self.trackers:
                await tracker()
        except Exception as exe:
            logger.error("%s: Error occurred in track method of Open Position for %d:%s",
                         exe, self.symbol.name, self.ticket)
