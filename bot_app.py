import asyncio
import os

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage
load_dotenv()
from bot.handlers.middleware import LoggingMiddleware
from aiogram import Bot, Dispatcher
import logging
from bot_instance import bot
from bot.handlers.user import user
from server.slots_scheduler import refresh_slots


scheduler = BackgroundScheduler()
scheduler.add_job(refresh_slots, "interval", minutes=1)
scheduler.start()
print("✅ Scheduler запущен (интервал 1 минута)")
refresh_slots()

async def main():
    await bot.delete_webhook(drop_pending_updates=True) #ignore previous messages
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.outer_middleware(LoggingMiddleware())
    dp.include_router(user)
    await dp.start_polling(bot)
    refresh_slots()


if __name__  == '__main__':
    logging.basicConfig(level=logging.INFO)
    print('Bot started!')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot interrupted!')