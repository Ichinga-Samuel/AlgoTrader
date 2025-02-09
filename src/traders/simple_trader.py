from logging import getLogger

from aiomql import OrderType, Trader


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
            exit_params = self.parameters.pop("exit_params", {})
            self.order.comment = parameters.get("name", "SimpleTrader")
            osr = await self.send_order()
            if osr.retcode != 10009 or osr is None:
                return
            # set the exit parameters for the trade
            self.config.state.setdefault("finger_trap_exit", {})[osr.order] = exit_params
            # set the exit at profit parameter for the trade
            self.config.state.setdefault("exit_at_profit", {})[osr.order] = parameters.get("exit_at_profit", 4)
            # set the exit at point parameter for the trade
            self.config.state.setdefault("exit_at_point", {})[osr.order] = parameters.get("exit_at_point", 100)
            self.parameters |= parameters
            await self.record_trade(result=osr, parameters=self.parameters.copy())
        except Exception as err:
            logger.error("%s for %s in %s.place_trade", err, self.symbol, self.__class__.__name__)
