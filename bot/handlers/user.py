import asyncio
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keybords.user_kb import main
from aiogram import F
import re
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from bot.states import AuthState
import httpx


EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@(?:yandex|gmail|outlook|icloud)\.(?:com|ru|by)$"
)

user = Router()

#catch states of user
# @user.message()
# async def debug_state(message: Message, state: FSMContext):
#     current_state = await state.get_state()
#     await message.answer(f"Текущее состояние: {current_state}")


@user.message(CommandStart())
async def start(message: Message):
    await message.answer('Please, choose country, which visa you would like to get?', reply_markup=main)

@user.message(F.text.in_(["USA", "Poland"]))
async def handle_country_choice(message: Message, state: FSMContext):
    await message.answer(f"You choose country: {message.text}")
    await state.set_state(AuthState.entering_email)
    await message.answer("Введите ваш email:")

@user.message(AuthState.entering_email)
async def get_email(message: Message, state: FSMContext):
    email = message.text
    if not EMAIL_REGEX.match(email):
        await message.answer(
            "Некорректный email.\nДопустимы только yandex, gmail, outlook, icloud с доменами .com, .ru, .by.\nПопробуйте снова:"
        )
        return
    await state.update_data(email=email)
    await state.set_state(AuthState.entering_password)
    await message.answer("Введите пароль:")

@user.message(AuthState.entering_password)
async def get_password(message: Message, state: FSMContext):
        password = message.text
        user_data = await state.get_data()
        email = user_data["email"]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8000/api/login", json={"email": email, "password": password})
                print(response)
                if response.status_code == 200:
                    await message.answer("Успешный вход! ✅", reply_markup=ReplyKeyboardRemove())
                    # Здесь — переход к следующему этапу, например, выбор даты
                else:
                    await message.answer("Ошибка авторизации. Проверьте данные.")
                    await state.set_state(AuthState.entering_email)
        except Exception as e:
            await message.answer("Ошибка подключения к серверу.")
            await state.clear()