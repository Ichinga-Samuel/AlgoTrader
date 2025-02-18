import asyncio
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, types
# from aiogram.utils import executor

API_TOKEN = '6645070821:AAGgdWAgnzO9jbS4_fRUFtByG4hMJM9woSM'

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher()


@dispatcher.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Welcome to the Aiogram bot!")


async def main():
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
