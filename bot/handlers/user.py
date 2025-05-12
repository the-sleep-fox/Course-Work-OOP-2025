from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keybords.user_kb import main
# import bot.keybords.user_kb as u_kb
from aiogram import F


user = Router()

@user.message(CommandStart())
async def start(message: Message):
    await message.answer('Please, choose country, which visa you would like to get?', reply_markup=main)

@user.message(F.text == "USA")
async def handle_country_choice(message: Message):
    await message.answer(f"Вы выбрали страну: {message.text}")

@user.message(F.text == "Poland")
async def handle_country_choice(message: Message):
    await message.answer(f"Вы выбрали страну: {message.text}")
