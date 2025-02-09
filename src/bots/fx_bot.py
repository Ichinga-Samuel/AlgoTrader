import logging

from aiomql import ForexSymbol, Bot

from ..strategies import FingerTrap
from ..trackers import exit_at_profit, exit_at_point, finger_trap_exit

logging.basicConfig(level=logging.INFO)


def fx_bot():
    # symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'EURGBP', 'EURCHF']
    symbols = ['Volatility 10 Index', 'Volatility 100 (1s) Index', 'Volatility 25 Index', 'Volatility 25 (1s) Index',
     'Volatility 75 Index', 'Volatility 10 (1s) Index', 'Volatility 75 (1s) Index', 'Volatility 50 Index',
     'Volatility 50 (1s) Index']
    syms = [ForexSymbol(name=symbol) for symbol in symbols]
    strategies = [FingerTrap(symbol=symbol) for symbol in syms]
    bot = Bot()  # create a bot instance
    bot.add_strategies(strategies=strategies)  # add the strategies to the bot
    # just to demonstrate the two main ways of adding trackers to the bot
    # exit_at_profit and exit_at_point are trackers that are added to the bot on the same thread
    # and both will run on the same event loop asynchronously
    bot.add_coroutine(coroutine=exit_at_profit, interval=5)  # add the exit at profit tracker
    bot.add_coroutine(coroutine=exit_at_point, interval=5)  # add the exit at point tracker
    # finger_trap_exit is a tracker that is added to the bot on a separate thread.
    # this is useful when you have a tracker that takes a long time to run and you don't want it to block the main
    # event loop, also for critical trackers that you don't want to be affected by the main event loop
    bot.add_coroutine(coroutine=finger_trap_exit, interval=60, on_separate_thread=True)
    bot.execute()
