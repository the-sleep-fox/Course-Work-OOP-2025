import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher
import logging
from bot.handlers.user import user

async def main():
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(user)
    await dp.start_polling(bot)


if __name__  == '__main__':
    logging.basicConfig(level=logging.INFO)
    print('Bot started!')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot interrupted!')