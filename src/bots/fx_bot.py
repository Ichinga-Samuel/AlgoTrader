import logging

from aiomql import ForexSymbol, Bot

from ..strategies import FingerTrap

logging.basicConfig(level=logging.INFO)


def fx_bot():
    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD', 'EURJPY', 'EURGBP', 'EURCHF']
    syms = [ForexSymbol(name=symbol) for symbol in symbols]
    strategies = [FingerTrap(symbol=symbol) for symbol in syms]
    bot = Bot()  # create a bot instance
    bot.add_strategies(strategies=strategies)  # add the strategies to the bot
    bot.execute()
