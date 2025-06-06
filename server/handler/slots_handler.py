import asyncio
import logging

import httpx
from aiogram import Bot
from bot_instance import bot

logger = logging.getLogger(__name__)

async def poll_slots_until_found(email, country, chat_id, session_id):
        print(f"👀 Запущен цикл поиска слотов для {email} в {country}...")
        cookies = {"session_id": session_id}
        while True:
            try:
                async with httpx.AsyncClient(
                        base_url="http://127.0.0.1:8000",
                        timeout=httpx.Timeout(30.0),
                        cookies=cookies,
                ) as client:
                    r = await client.get(f"/{country}/slots")
                    if r.status_code == 200:
                        slots = r.json().get("slots", [])
                        if slots:
                            slot = slots[0]
                            book = await client.post("/select_slot", json={
                                "date": slot["date"],
                                "time": slot["time"],
                                "email": email,
                                "country": country
                            })
                            if book.status_code == 200:
                                await bot.send_message(chat_id, f"Слот забронирован: {slot['date']} {slot['time']} 📅")
                                return book.json()
                            else:
                                await bot.send_message(chat_id,
                                    f"Ошибка бронирования: {book.json().get('detail', 'Неизвестная ошибка')}")
                                return None
                    elif r.status_code == 401:
                        await bot.send_message(chat_id, "Сессия истекла. Пожалуйста, войдите снова.")
                        return None
                    await asyncio.sleep(60)  # Пауза перед следующим запросом
            except httpx.RequestError as e:
                print(f"❌ Ошибка запроса: {e}")
                await asyncio.sleep(60)
            except Exception as e:
                print(f"❌ Неизвестная ошибка: {e}")
                await asyncio.sleep(60)
