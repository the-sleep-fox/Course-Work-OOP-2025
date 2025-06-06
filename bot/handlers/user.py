import asyncio
import re
from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types.keyboard_button import KeyboardButton
import httpx
import logging
from aiogram import F

from bot.states import RegisterStates, AuthState
from server.handler.slots_handler import poll_slots_until_found

user = Router()
logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Мои записи")],
        [KeyboardButton(text="❌ Отменить запись")],
        [KeyboardButton(text="🌍 Получить новую запись")],
        [KeyboardButton(text="🚪 Выйти")]
    ], resize_keyboard=True
)


# Стартовое сообщение
@user.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добро пожаловать! Войдите или зарегистрируйтесь:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🔐 Войти")],
                [KeyboardButton(text="🆕 Зарегистрироваться")]
            ],
            resize_keyboard=True
        )
    )

# Начало логина
@user.message(StateFilter(None), F.text == "🔐 Войти")
async def login(message: Message, state: FSMContext):
    await message.answer("Введите email:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AuthState.entering_email)

# Получение email
@user.message(AuthState.entering_email)
async def get_email(message: Message, state: FSMContext):
    email = message.text.strip()
    logger.info(f"Введен email: {email}")
    if not EMAIL_REGEX.match(email):
        await message.answer("Некорректный email. Попробуйте снова:")
        return
    await state.update_data(email=email)
    await message.answer("Введите пароль:")
    await state.set_state(AuthState.entering_password)

# Получение пароля и логин
@user.message(AuthState.entering_password)
async def get_password(message: Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    email = user_data["email"]
    logger.info(f"Попытка логина: email={email}, Chat ID: {message.chat.id}, User ID: {message.from_user.id}")

    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=httpx.Timeout(30.0)) as client:
            response = await client.post("/auth/login", json={"email": email, "password": password})
            response.raise_for_status()
            session_id = response.cookies.get("session_id")
            if not session_id:
                logger.error("Cookie session_id не найдено в ответе")
                await message.answer("Ошибка сервера: сессия не создана. Попробуйте снова.")
                return
            logger.info(f"Сохранено: State={await state.get_state()}, Data={await state.get_data()}")
            await state.update_data(session_id=session_id)
            await state.set_state(AuthState.menu)
            await message.answer("Вход успешен! Выберите действие:", reply_markup=main_menu)
    except httpx.HTTPStatusError as e:
        error_detail = e.response.json().get("detail", "Ошибка входа")
        logger.error(f"HTTP ошибка: {e.response.status_code}, Детали: {error_detail}")
        await message.answer(f"Ошибка входа: {error_detail}. Попробуйте снова.")
    except httpx.RequestError as e:
        logger.error(f"Ошибка запроса: {e}")
        await message.answer("Ошибка соединения с сервером. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при логине: {type(e).__name__}: {e}")
        await message.answer("Произошла неизвестная ошибка. Попробуйте позже.")

# Выход из аккаунта
@user.message(AuthState.menu, F.text == "🚪 Выйти")
async def logout(message: Message, state: FSMContext):
    user_data = await state.get_data()
    session_id = user_data.get("session_id")
    if not session_id:
        await message.answer("Вы не авторизованы.")
        await state.clear()
        await message.answer(
            "Войдите снова или зарегистрируйтесь:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔐 Войти")],
                          [KeyboardButton(text="🆕 Зарегистрироваться")]],
                resize_keyboard=True
            )
        )
        return
    cookies = {"session_id": session_id}
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=httpx.Timeout(30.0), cookies=cookies) as client:
        try:
            response = await client.post("/auth/logout")
            response.raise_for_status()
            await state.clear()
            await message.answer(
                "Выход успешен. Войдите снова:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="🔐 Войти")],
                              [KeyboardButton(text="🆕 Зарегистрироваться")]],
                    resize_keyboard=True
                )
            )
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Ошибка выхода")
            logger.error(f"HTTP ошибка при выходе: {e.response.status_code}, Детали: {error_detail}")
            await message.answer(f"Ошибка выхода: {error_detail}")
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса при выходе: {e}")
            await message.answer("Ошибка соединения с сервером. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при выходе: {type(e).__name__}: {e}")
            await message.answer("Произошла неизвестная ошибка. Попробуйте позже.")

# Просмотр записей
@user.message(AuthState.menu, F.text == "📄 Мои записи")
async def view_bookings(message: Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data.get("email")
    session_id = user_data.get("session_id")
    if not session_id:
        await message.answer("Сессия истекла. Пожалуйста, войдите снова.")
        await state.clear()
        await message.answer(
            "Войдите снова:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔐 Войти")],
                          [KeyboardButton(text="🆕 Зарегистрироваться")]],
                resize_keyboard=True
            )
        )
        return
    cookies = {"session_id": session_id}
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=httpx.Timeout(30.0), cookies=cookies) as client:
        try:
            response = await client.get(f"/get_bookings?email={email}")
            response.raise_for_status()
            bookings = response.json().get("bookings", [])
            if bookings:
                msg = "Ваши записи:\n" + "\n".join([f"{b['country']}: {b['date']} {b['time']}" for b in bookings])
            else:
                msg = "У вас нет активных записей."
            await message.answer(msg, reply_markup=main_menu)
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Ошибка получения записей")
            logger.error(f"HTTP ошибка: {e.response.status_code}, Детали: {error_detail}")
            if e.response.status_code == 401:
                await message.answer("Сессия истекла. Пожалуйста, войдите снова.")
                await state.clear()
            else:
                await message.answer(f"Ошибка: {error_detail}")
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса: {e}")
            await message.answer("Ошибка соединения с сервером. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при получении записей: {type(e).__name__}: {e}")
            await message.answer("Произошла неизвестная ошибка. Попробуйте позже.")

# Запрос на отмену записи
@user.message(AuthState.menu, F.text == "❌ Отменить запись")
async def ask_cancel_country(message: Message, state: FSMContext):
    await message.answer("Введите страну, запись в которую вы хотите отменить:")
    await state.set_state(AuthState.canceling_country)

# Отмена записи
@user.message(AuthState.canceling_country)
async def cancel_booking(message: Message, state: FSMContext):
    country = message.text.lower()
    user_data = await state.get_data()
    email = user_data.get("email")
    session_id = user_data.get("session_id")
    if not session_id:
        await message.answer("Сессия истекла. Пожалуйста, войдите снова.")
        await state.clear()
        await message.answer(
            "Войдите снова:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔐 Войти")],
                          [KeyboardButton(text="🆕 Зарегистрироваться")]],
                resize_keyboard=True
            )
        )
        return
    cookies = {"session_id": session_id}
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=httpx.Timeout(30.0), cookies=cookies) as client:
        try:
            response = await client.delete("/cancel_booking", params={"email": email, "country": country})
            response.raise_for_status()
            await message.answer("Запись успешно отменена.", reply_markup=main_menu)
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Ошибка отмены записи")
            logger.error(f"HTTP ошибка: {e.response.status_code}, Детали: {error_detail}")
            if e.response.status_code == 401:
                await message.answer("Сессия истекла. Пожалуйста, войдите снова.")
                await state.clear()
            else:
                await message.answer(f"❌ Ошибка: {error_detail}")
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса: {e}")
            await message.answer("Ошибка соединения с сервером. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при отмене записи: {type(e).__name__}: {e}")
            await message.answer("Произошла неизвестная ошибка. Попробуйте позже.")
    await state.set_state(AuthState.menu)

# Запрос на новую запись
@user.message(AuthState.menu, F.text == "🌍 Получить новую запись")
async def ask_country_for_booking(message: Message, state: FSMContext):
    await message.answer("Выберите страну: USA или Poland")
    await state.set_state(AuthState.entering_country)

# Выбор страны и бронирование
@user.message(AuthState.entering_country)
async def handle_country_choice(message: Message, state: FSMContext):
    country = message.text.lower()
    if country not in ["usa", "poland"]:
        await message.answer("Неверная страна. Выберите: USA или Poland")
        return

    user_data = await state.get_data()
    email = user_data.get("email")
    session_id = user_data.get("session_id")
    if not session_id:
        await message.answer("Сессия истекла. Пожалуйста, войдите снова.")
        await state.clear()
        await message.answer(
            "Войдите снова:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔐 Войти")]],
                resize_keyboard=True
            )
        )
        return
    cookies = {"session_id": session_id}
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=httpx.Timeout(30.0), cookies=cookies) as client:
        try:
            slots_response = await client.get(f"/{country}/slots")
            slots_response.raise_for_status()
            slots_data = slots_response.json()
            slots = slots_data.get("slots", [])
            if not slots:
                await message.answer("Нет доступных слотов сейчас. Начинаю отслеживание ⏳...")
                chat_id = message.chat.id
                # Передаем session_id вместо cookies
                asyncio.create_task(
                    poll_slots_until_found(
                        email=email,
                        country=country,
                        chat_id=chat_id,
                        session_id=session_id  # Изменено
                    )
                )
                await state.set_state(AuthState.menu)
                return

            first_slot = slots[0]
            book_response = await client.post("/select_slot", json={
                "date": first_slot["date"],
                "time": first_slot["time"],
                "email": email,
                "country": country
            })
            book_response.raise_for_status()
            await message.answer(
                f"Слот забронирован: {first_slot['date']} {first_slot['time']} 📅",
                reply_markup=main_menu
            )
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Ошибка бронирования")
            logger.error(f"HTTP ошибка: {e.response.status_code}, Детали: {error_detail}")
            if e.response.status_code == 401:
                await message.answer("Сессия истекла. Пожалуйста, войдите снова.")
                await state.clear()
            else:
                await message.answer(f"Ошибка: {error_detail}")
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса: {e}")
            await message.answer("Ошибка соединения с сервером. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при бронировании: {type(e).__name__}: {e}")
            await message.answer("Произошла неизвестная ошибка. Попробуйте позже.")
    await state.set_state(AuthState.menu)

# Начало регистрации
@user.message(StateFilter(None), F.text == "🆕 Зарегистрироваться")
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(RegisterStates.waiting_for_email)
    await message.answer("Введите ваш email:", reply_markup=ReplyKeyboardRemove())

# Обработка email при регистрации
@user.message(RegisterStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    if not EMAIL_REGEX.match(email):
        await message.answer("Неверный формат email. Попробуйте снова:")
        return
    await state.update_data(email=email)
    await state.set_state(RegisterStates.waiting_for_passport)
    await message.answer("Введите номер паспорта (например, AB1234567):")

# Обработка паспорта
@user.message(RegisterStates.waiting_for_passport)
async def process_passport(message: Message, state: FSMContext):
    passport_id = message.text.strip().upper()
    if not re.match(r"^[A-Z]{2}\d{7}$", passport_id):
        await message.answer("Неверный формат номера паспорта. Ожидается: AB1234567. Попробуйте снова:")
        return
    await state.update_data(passport_id=passport_id)
    await state.set_state(RegisterStates.waiting_for_password)
    await message.answer("Введите пароль (минимум 8 символов):")

# Обработка пароля
@user.message(RegisterStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    if len(password) < 8:
        await message.answer("Пароль должен содержать минимум 8 символов. Попробуйте снова:")
        return
    await state.update_data(temp_password=password)
    await state.set_state(RegisterStates.waiting_for_password_confirm)
    await message.answer("Повторите пароль для подтверждения:")

# Подтверждение пароля
@user.message(RegisterStates.waiting_for_password_confirm)
async def confirm_password(message: Message, state: FSMContext):
    confirm_password = message.text.strip()
    user_data = await state.get_data()
    original_password = user_data.get("temp_password")
    if confirm_password != original_password:
        await message.answer("Пароли не совпадают. Введите пароль заново:")
        await state.set_state(RegisterStates.waiting_for_password)
        return

    email = user_data["email"]
    passport_id = user_data["passport_id"]
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=httpx.Timeout(30.0)) as client:
        try:
            response = await client.post("/auth/register", json={
                "email": email,
                "passport_id": passport_id,
                "password": original_password
            })
            response.raise_for_status()
            await message.answer(
                "✅ Регистрация успешна! Теперь вы можете войти.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="🔐 Войти")],
                              [KeyboardButton(text="🆕 Зарегистрироваться")]],
                    resize_keyboard=True
                )
            )
            await state.clear()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Ошибка регистрации")
            logger.error(f"HTTP ошибка: {e.response.status_code}, Детали: {error_detail}")
            if "Пользователь с таким" in error_detail:
                await message.answer(
                    f"Ошибка: {error_detail}. Начните заново:",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="⬅ Начать заново")]
                        ],
                        resize_keyboard=True
                    )
                )
                await state.set_state(RegisterStates.waiting_for_retry)
            else:
                await message.answer(f"Ошибка регистрации: {error_detail}. Попробуйте снова.", reply_markup=main_menu)
                await state.clear()
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса: {e}")
            await message.answer("Ошибка соединения с сервером. Попробуйте позже.", reply_markup=main_menu)
            await state.clear()
        except Exception as e:
            logger.error(f"Неизвестная ошибка при регистрации: {type(e).__name__}: {e}")
            await message.answer("Произошла неизвестная ошибка. Попробуйте позже.", reply_markup=main_menu)
            await state.clear()

@user.message(StateFilter(None), F.text)
async def handle_unknown_command(message: Message, state: FSMContext):
    await message.answer(
        "Неизвестная команда. Выберите действие:", reply_markup=main_menu
    )

@user.message(RegisterStates.waiting_for_retry, F.text == "⬅ Начать заново")
async def restart_registration(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите ваш email:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterStates.waiting_for_email)
