import logging

from aiomql import Symbol, Strategy, TimeFrame, Sessions, OrderType, Trader, Tracker, Candles, RAM

from ..traders import SimpleTrader
from ..utils.candle_patterns import swing_low, swing_high

logger = logging.getLogger(__name__)


# all strategies must inherit from Strategy and implement a trade method, which will be called at each iteration.
class FingerTrap(Strategy):
    ttf: TimeFrame
    etf: TimeFrame
    fast_ema: int
    slow_ema: int
    entry_ema: int
    ecc: int
    tcc: int
    trader: Trader
    tracker: Tracker
    interval: TimeFrame = TimeFrame.H1

    # The default parameters for the strategy. You can override these in the constructor.
    # via the `params` argument as a dictionary.
    # using two weeks of data for the fast and slow ema
    parameters = {"fast_ema": 8, "slow_ema": 34, "etf": TimeFrame.M5, "ttf": TimeFrame.M5,
                  "entry_ema": 5, "tcc": 1344, "ecc": 4032}

    def __init__(self, *, symbol: Symbol, params: dict | None = None, trader: Trader = None, sessions: Sessions = None,
                 name: str = "FingerTrap"):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        # use the ram instance to set the minimum and maximum amount to trade and the risk to reward ratio
        ram = RAM(min_amount=5, max_amount=10, risk_to_reward=1)
        self.trader = trader or SimpleTrader(symbol=self.symbol, ram=ram)
        # a dataclass object that maintains the state of the strategy from iteration to iteration
        self.tracker: Tracker = Tracker(snooze=self.ttf.seconds)

        # add the parameters for the exit function to parameters
        self.parameters["exit_params"] = {"timeframe": TimeFrame.M5, "count": 1344, "ema": 5}

    async def initialize(self):
        """Initialize the strategy. Wait till the beginning of the next timeframe before starting the strategy."""
        await self.sleep(secs=self.ttf.seconds)

    async def check_trend(self):
        """
        Check the current trend of the market in the higher timeframe. Determine if the market is bullish, bearish or
        ranging an update the tracker, if market is not in trend then set the snooze time to the timeframe seconds.
        """
        try:
            # get the candles for the higher timeframe
            candles: Candles = await self.symbol.copy_rates_from_pos(timeframe=self.ttf, count=self.tcc)

            # calculate the fast and slow ema and rename the columns to fast and slow
            candles.ta.ema(length=self.slow_ema, append=True, fillna=0)
            candles.ta.ema(length=self.fast_ema, append=True, fillna=0)
            candles.rename(inplace=True, **{f"EMA_{self.fast_ema}": "fast", f"EMA_{self.slow_ema}": "slow"})

            # for uptrend check if the close is above the fast ema and the fast ema is above the slow ema
            # check if the close is above the fast ema
            caf = candles.ta_lib.above(candles.close, candles.fast)
            # check if the fast ema is above the slow ema
            fas = candles.ta_lib.above(candles.fast, candles.slow)

            # for downtrend check if the close is below the fast ema and the fast ema is below the slow ema
            # check if the close is below the fast ema for bearish trend
            cbf = candles.ta_lib.below(candles.close, candles.fast)
            # check if the fast ema is below the slow ema for bearish trend
            fbs = candles.ta_lib.below(candles.fast, candles.slow)

            # confirm the trend by checking the last bars
            if fas.iloc[-1] and caf.iloc[-1]:
                self.tracker.update(trend="bullish")

            # if the last two fit the bearish trend then update the tracker with the bearish trend
            elif fbs.iloc[-1] and cbf.iloc[-1]:
                self.tracker.update(trend="bearish")

            # if the last two candles are ranging then update the tracker with the ranging trend
            else:
                self.tracker.update(trend=self.ttf.seconds, snooze=self.ttf.seconds, order_type=None)
        except Exception as err:
            logger.error("%s: Error in %s.check_trend", err, self.__class__.__name__)
            self.tracker.update(snooze=self.ttf.seconds, order_type=None)

    async def confirm_trend(self):
        """Check the lower timeframe to confirm the trend and place the trade"""
        try:
            candles = await self.symbol.copy_rates_from_pos(timeframe=self.etf, count=self.ecc)

            # calculate the entry ema and rename the column to ema
            candles.ta.ema(length=self.entry_ema, append=True)
            candles.rename(**{f"EMA_{self.entry_ema}": "ema"})

            # check for crossover and cross_under
            candles['cae'] = candles.ta_lib.cross(candles.close, candles.ema)
            candles['cbe'] = candles.ta_lib.cross(candles.close, candles.ema, above=False)
            current = candles[-1]
            if self.tracker.bullish and current.cae:
                # get the most recent swing low
                sl_candle = swing_low(candles=candles, n=1)
                sl = sl_candle.low
                # after placing the trade wait for the interval seconds before placing another trade
                self.tracker.update(snooze=self.interval.seconds, order_type=OrderType.BUY, sl=sl)
            elif self.tracker.bearish and current.cbe:
                # get the most recent swing high
                sl_candle = swing_high(candles=candles, n=1)
                sl = sl_candle.high
                self.tracker.update(snooze=self.interval.seconds, order_type=OrderType.SELL, sl=sl)
            else:
                self.tracker.update(snooze=self.etf.seconds, order_type=None)
        except Exception as err:
            logger.error(f"{err} for {self.symbol} in {self.__class__.__name__}.confirm_trend")
            self.tracker.update(snooze=self.etf.seconds, order_type=None)

    async def watch_market(self):
        # check the trend of the market
        await self.check_trend()
        # if the market is not bullish or bearish then confirm the trend and enter the trade
        if self.tracker.ranging is False:
            await self.confirm_trend()

    async def trade(self):
        try:
            await self.watch_market()
            # if the order type is not None then place the trade
            if self.tracker.order_type is not None:
                await self.trader.place_trade(order_type=self.tracker.order_type,
                                              parameters=self.parameters, sl=self.tracker.sl)

            await self.sleep(secs=self.tracker.snooze)

        except Exception as err:
            logger.error("%s: Error for %s in %s.trade", err, self.symbol, self.__class__.__name__)
            await self.sleep(secs=self.ttf.seconds)
