import asyncio
import os
from dotenv import load_dotenv
import logging

load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Первое сообщение')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("Bot started")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")

