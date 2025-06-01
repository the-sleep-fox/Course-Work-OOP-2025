from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from bot.keybords.countries.poland import poland_row
# from bot.keybords.countries.usa import usa_row


main= ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌍 Найти слот")],
        [KeyboardButton(text="📄 Мои записи"), KeyboardButton(text="❌ Отменить запись")],
        [KeyboardButton(text="🔐 Зарегистрироваться")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)
