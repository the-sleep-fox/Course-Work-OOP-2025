import asyncio
import os

import redis
from dotenv import load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage
load_dotenv()
from bot.handlers.middleware import LoggingMiddleware
from aiogram import Bot, Dispatcher
import logging
from bot_instance import bot
from bot.handlers.user import user
from aiogram.fsm.storage.redis import RedisStorage

storage = RedisStorage.from_url("redis://localhost:6379/1")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        dp = Dispatcher(storage=storage)
        logger.info("Подключение к Redis успешно")
        dp.update.outer_middleware(LoggingMiddleware())
        dp.include_router(user)
        await dp.start_polling(bot)
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Ошибка подключения к Redis: {e}")
        print(f"Ошибка подключения к Redis: {e}")
        print("Запустите redis-server или проверьте конфигурацию.")
        exit(1)


if __name__  == '__main__':
    logging.basicConfig(level=logging.INFO)
    print('Bot started!')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot interrupted!')