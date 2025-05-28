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
async def start(message: Message, state: FSMContext):
    await state.set_state(AuthState.entering_country)
    await message.answer('Please, choose country, which visa you would like to get?', reply_markup=main)

@user.message(F.text.in_(["USA", "Poland"]))
async def handle_country_choice(message: Message, state: FSMContext):
    country = message.text
    await message.answer(f"You choose country: {message.text}")
    await state.update_data(country=country)
    await state.set_state(AuthState.entering_email)
    await message.answer("Введите ваш email:", reply_markup=ReplyKeyboardRemove())

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
    country = user_data["country"].lower()

    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
            # Логин
            response = await client.post("/auth/login", json={"email": email, "password": password})

            if response.status_code == 200:
                data = response.json()
                msg = data.get("message", "Успешный вход!")
                await message.answer(f"{msg} ✅\nВы вошли как: {data.get('user')}")

                # Переход на страницу слотов
                slots_response = await client.get(f"/{country}/slots", cookies=response.cookies)
                await message.answer(f"Перехожу на страницу слотов!")
                if slots_response.status_code == 200:
                    slots_data = slots_response.json()
                    slots = slots_data.get("slots", [])
                    await message.answer(f"slots: {slots}")

                    if not slots:
                        await message.answer("Нет доступных слотов 😢. Попробуйте позже.")
                        return

                    # Выбор первого слота
                    first_slot = slots[0]
                    await message.answer(f"first slot: {first_slot}")
                    book_response = await client.post("/select_slot", json={
                        "date": first_slot[0],
                        "time": first_slot[1],
                        "email": email,
                        "country": country
                    }, cookies=response.cookies)

                    if book_response.status_code == 200:
                        await message.answer(f"Слот забронирован: {first_slot[0]} {first_slot[1]} 📅")
                    else:
                        await message.answer("Не удалось забронировать слот. Возможно, он уже занят.")

                else:
                    await message.answer("Ошибка загрузки слотов.")

                await state.clear()
            else:
                await message.answer("Ошибка авторизации. Проверьте данные.")
                await state.set_state(AuthState.entering_email)

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Ошибка подключения к серверу.")
        await state.clear()
