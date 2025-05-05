from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import bot.countries.poland as pl
import bot.countries.usa as us

user = Router()

@user.message(CommandStart())
async def start(message: Message):
    combined_markup = ReplyKeyboardMarkup(
        keyboard=[
            pl.poland_row,  # Row from Poland
            us.usa_row,     # Row from USA
            [KeyboardButton(text="Back")]  # Additional row
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose country"
    )
    await message.answer(
        "Please choose a country:",
        reply_markup=combined_markup
    )