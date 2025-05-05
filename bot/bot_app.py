import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher

from handlers.user import user

import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent))

async def main():
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(user)
    await dp.start_polling(bot)


if __name__  == '__main__':
    print('Bot started!')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot interrupted!')