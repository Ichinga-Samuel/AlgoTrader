from pprint import pprint as pp
import asyncio
import logging
from argparse import ArgumentParser

from aiogram import Bot, Dispatcher, html, Router, MagicFilter
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyParameters, ForceReply


TOKEN = "6645070821:AAGgdWAgnzO9jbS4_fRUFtByG4hMJM9woSM"
# @OdogwuBot id=6645070821
chat_id = 5661902616
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    """Handle /start command"""
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def order_handler(message: Message):
    """Handle all messages"""
    # print(message)
    # pp(dir(message))
    # message.chat is the details of the chat, mostly that of the sender
    # message.from_user is the details of the sender
    b1 = KeyboardButton(text="Click me!")
    b2 = KeyboardButton(text="double Click me!")
    keyboard = ReplyKeyboardMarkup(keyboard=[[b1, b2]], resize_keyboard=True)
    # kb = ReplyKeyboardMarkup( resize_keyboard=True)
    # button = InlineKeyboardButton(text="Click me!", callback_data='A')
    # button2 = InlineKeyboardButton(text="Click me!", callback_data='B')
    # keyboard = InlineKeyboardMarkup(inline_keyboard=[button, button2])

    # keyboard.add(button)
    # keyboard.add(button2)
    print(message.text, message.reply_to_message, message.chat.id, message.from_user.id)
    await message.answer("Choose", reply_markup=keyboard)


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("--token", help="Telegram Bot API Token")
    parser.add_argument("--chat-id", type=int, help="Target chat id")
    parser.add_argument("--message", "-m", help="Message text to sent", default="Hello, World!")

    return parser


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    b1 = InlineKeyboardButton(text="cancel", callback_data='cancel')
    b2 = InlineKeyboardButton(text="Ok", callback_data='ok')
    kb = InlineKeyboardMarkup(inline_keyboard=[[b1, b2]])
    router = Router()
    # keyboard = ReplyKeyboardMarkup(keyboard=[[b1, b2]], one_time_keyboard=True,
                                   # resize_keyboard=True)
    # ForceReply(input_field_placeholder='ok')
    msg = await bot.send_message(chat_id=chat_id, text='place trade', reply_markup=ForceReply(input_field_placeholder='ok'))

    # await bot.edit_message_reply_markup(message_id=msg.message_id, chat_id=chat_id)
    # pp(msg.model_dump())
    msg_id = msg.message_id
    print(msg_id, 'message id')
    await asyncio.sleep(10)
    # res = await bot.get_chat(chat_id)
    ups = await bot.get_updates(offset=704666151)
    for up in ups:
        if (res:=up.message.reply_to_message) and res.message_id == msg_id:
            print(up.update_id, res.message_id, msg_id, up.message.text, res.text)
    # pp(res.model_dump())
    # await bot.close()
    # bot.
    # And the run events dispatching
    # await dp.start_polling(bot)


async def pmain():
    parser = create_parser()
    ns = parser.parse_args()

    token = ns.token
    chat_id = ns.chat_id
    message = ns.message

    async with Bot(
        token=token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    ) as bot:
        await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
