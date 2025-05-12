from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
import bot.keybords.user_kb as u_kb

user = Router()

@user.message(CommandStart())
async def start(message: Message):
    await message.answer('Please, choose country, which visa you would like to get?', reply_markup=u_kb.main)