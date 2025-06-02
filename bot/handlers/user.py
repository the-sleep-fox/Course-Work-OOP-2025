import asyncio
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from aiogram import F
import re
from aiogram.fsm.context import FSMContext
from bot.states import AuthState, RegisterStates
import httpx

from server.handler.slots_handler import poll_slots_until_found
from ..keybords.user_kb import main
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@(?:yandex|gmail|outlook|icloud)\.(?:com|ru|by)$"
)

user = Router()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Мои записи")],
        [KeyboardButton(text="❌ Отменить запись")],
        [KeyboardButton(text="🌍 Получить новую запись")]
    ], resize_keyboard=True
)

@user.message(CommandStart())
async def start(message: Message, state: FSMContext):
    # chat_id = message.chat.id
    # await message.answer(f"Ваш chat_id: {chat_id}")
    await state.clear()
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔐 Войти")],
            [KeyboardButton(text="\U0001F195 Зарегистрироваться")],
        ], resize_keyboard=True
    ))

@user.message(F.text == "🔐 Войти")
async def login_start(message: Message, state: FSMContext):
    await message.answer("Введите ваш email:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AuthState.entering_email)

@user.message(AuthState.entering_email)
async def get_email(message: Message, state: FSMContext):
    email = message.text
    if not EMAIL_REGEX.match(email):
        await message.answer("Некорректный email. Попробуйте снова:")
        return
    await state.update_data(email=email)
    await message.answer("Введите пароль:")
    await state.set_state(AuthState.entering_password)

@user.message(AuthState.entering_password)
async def get_password(message: Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    email = user_data["email"]

    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
            response = await client.post("/auth/login", json={"email": email, "password": password})
            if response.status_code == 200:
                data = response.json()
                await message.answer(f"Успешный вход ✅\nВы вошли как: {data.get('user')}", reply_markup=main_menu)
                await state.set_state(AuthState.menu)
            else:
                await message.answer("Ошибка авторизации. Проверьте данные.")
                await state.set_state(AuthState.entering_email)
    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Ошибка подключения к серверу.")
        await state.clear()

@user.message(AuthState.menu, F.text == "📄 Мои записи")
async def view_bookings(message: Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data.get("email")
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.get(f"/get_bookings?email={email}")
        if response.status_code == 200:
            bookings = response.json().get("bookings", [])
            if bookings:
                msg = "Ваши записи:\n" + "\n".join([f"{b['country']}: {b['date']} {b['time']}" for b in bookings])
            else:
                msg = "У вас нет активных записей."
            await message.answer(msg)
        else:
            await message.answer("Не удалось получить записи.")

@user.message(AuthState.menu, F.text == "❌ Отменить запись")
async def ask_cancel_country(message: Message, state: FSMContext):
    await message.answer("Введите страну, запись в которую вы хотите отменить:")
    await state.set_state(AuthState.canceling_country)

@user.message(AuthState.canceling_country)
async def cancel_booking(message: Message, state: FSMContext):
    country = message.text.lower()
    user_data = await state.get_data()
    email = user_data.get("email")
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.delete(
            "/cancel_booking", params={"email": email, "country": country}
        )
        if response.status_code == 200:
            await message.answer("Запись успешно отменена.", reply_markup=main_menu)
        else:
            try:
                error_data = response.json()
                detail = error_data.get("detail", "Ошибка сервера.")
                await message.answer(f"❌ Ошибка: {detail}")
            except Exception:
                await message.answer("⚠️ Произошла неизвестная ошибка.")
    await state.set_state(AuthState.menu)

@user.message(AuthState.menu, F.text == "🌍 Получить новую запись")
async def ask_country_for_booking(message: Message, state: FSMContext):
    await message.answer("Выберите страну: USA или Poland")
    await state.set_state(AuthState.entering_country)

@user.message(AuthState.entering_country)
async def handle_country_choice(message: Message, state: FSMContext):
    country = message.text.lower()
    if country not in ["usa", "poland"]:
        await message.answer("Неверная страна. Выберите: USA или Poland")
        return

    user_data = await state.get_data()
    email = user_data["email"]


    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        slots_response = await client.get(f"/{country}/slots")
        if slots_response.status_code == 200:
            slots_data = slots_response.json()
            slots = slots_data.get("slots", [])
            if not slots:
                await message.answer("Нет доступных слотов сейчас. Начинаю отслеживание ⏳...")
                chat_id = message.chat.id
                asyncio.create_task(
                    poll_slots_until_found(email=email, country=country,chat_id=chat_id,
                                           cookies=slots_response.cookies)
                )
                await state.clear()
                return

            first_slot = slots[0]
            book_response = await client.post("/select_slot", json={
                "date": first_slot["date"],
                "time": first_slot["time"],
                "email": email,
                "country": country
            })
            print("book response: ", book_response)
            if book_response.status_code == 200:
                await message.answer(f"Слот забронирован: {first_slot["date"]} {first_slot["time"]} 📅", reply_markup=main_menu)
            else:
                await message.answer("Не удалось забронировать слот. Попробуйте позже.")
        else:
            await message.answer("Ошибка получения слотов.")
    await state.set_state(AuthState.menu)

@user.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔐 Войти")],
            [KeyboardButton(text="\U0001F195 Зарегистрироваться")],
        ], resize_keyboard=True
    ))

@user.message(F.text == "\U0001F195 Зарегистрироваться")
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(RegisterStates.waiting_for_email)
    await message.answer("Введите ваш email:", reply_markup=ReplyKeyboardRemove())

@user.message(RegisterStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    # Простая проверка формата email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await message.answer("Неверный формат email. Попробуйте снова:")
        return
    await state.update_data(email=email)
    await state.set_state(RegisterStates.waiting_for_passport)
    await message.answer("Введите номер паспорта (например, AB1234567):")

@user.message(RegisterStates.waiting_for_passport)
async def process_passport(message: Message, state: FSMContext):
    passport_id = message.text.strip().upper()
    # Проверка формата паспорта
    if not re.match(r"^[A-Z]{2}\d{7}$", passport_id):
        await message.answer("Неверный формат номера паспорта. Ожидается: AB1234567. Попробуйте снова:")
        return
    await state.update_data(passport_id=passport_id)
    await state.set_state(RegisterStates.waiting_for_password)
    await message.answer("Введите пароль (минимум 8 символов):")

@user.message(RegisterStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    if len(password) < 8:
        await message.answer("Пароль должен содержать минимум 8 символов. Попробуйте снова:")
        return

    user_data = await state.get_data()
    email = user_data["email"]
    passport_id = user_data["passport_id"]

    # Отправка запроса на регистрацию
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        try:
            response = await client.post("http://127.0.0.1:8000/auth/register", json={
                "email": email,
                "passport_id": passport_id,
                "password": password
            })
            response.raise_for_status()  # Вызовет исключение для кодов 4xx/5xx
            await message.answer("Регистрация успешна! Теперь вы можете войти.", reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔐 Войти")]], resize_keyboard=True
            ))
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Ошибка регистрации")
            await message.answer(f"Ошибка регистрации: {error_detail}. Попробуйте снова.")
        except httpx.RequestError as e:
            await message.answer("Ошибка соединения с сервером. Попробуйте позже.")
            print(f"❌ Ошибка запроса: {e}")
        except Exception as e:
            await message.answer("Произошла неизвестная ошибка. Попробуйте позже.")
            print(f"❌ Неизвестная ошибка: {e}")

    await state.clear()