from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.countries import poland, usa

user = Router()

@user.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello! I'm bot for booking visa-appointment time-slot")
    await message.answer("Please, choose on of countries, that visa you would like to become:", pol_markup=poland.main, usa_markup=usa.main)
