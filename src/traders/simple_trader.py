from logging import getLogger

from aiomql import OrderType, Trader, TradePosition

from ..data_structs import PositionTracker, OpenPosition
from ..trackers import finger_exit, exit_at_profit, exit_at_point, atr_trailer

logger = getLogger(__name__)


class SimpleTrader(Trader):
    """Simple trader class for placing trades"""
    async def place_trade(self, order_type: OrderType, sl: float, parameters: dict = None):
        try:
            # uses the amount as gotten from the RAM instance to determine the amount to risk and volume to trade
            # take profit is gotten from the risk_to_reward_ratio attribute of the RAM instance
            await self.create_order_with_sl(order_type=order_type, sl=sl)
            parameters = parameters or {}
            # get the exit parameters from the parameters dictionary
            exit_params = parameters.pop("exit_params", {})
            self.order.comment = parameters.get("name", "SimpleTrader")
            osr = await self.send_order()
            if osr.retcode != 10009 or osr is None:
                return
            open_pos = OpenPosition(ticket=osr.order, symbol=self.symbol,
                                    position=TradePosition(ticket=osr.order, symbol=self.symbol.name))
            open_pos.add_tracker(tracker=PositionTracker(exit_at_point, points=50)) # 50 points
            open_pos.add_tracker(tracker=PositionTracker(exit_at_profit))
            open_pos.add_tracker(tracker=PositionTracker(finger_exit, **exit_params))
            open_pos.add_tracker(tracker=PositionTracker(atr_trailer))
            self.parameters |= parameters
            await self.record_trade(result=osr, parameters=self.parameters.copy())
        except Exception as err:
            logger.error("%s for %s in %s.place_trade", err, self.symbol, self.__class__.__name__)
