from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from bot.keybords.countries.poland import poland_row
# from bot.keybords.countries.usa import usa_row


main = ReplyKeyboardMarkup(keyboard = [KeyboardButton(text="Poland"), KeyboardButton(text="USA")],
                           resize_keyboard=True, input_field_placeholder="Choose country")
