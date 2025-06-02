import asyncio
import httpx
from aiogram import Bot
from bot_instance import bot


async def poll_slots_until_found(email, country, chat_id, cookies):
    print("👀 Запущен цикл поиска слотов...")
    while True:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
            r = await client.get(f"/{country}/slots", cookies=cookies)
            print("r status code: ",r.status_code)
            if r.status_code == 200:
                slots = r.json().get("slots", [])
                print(slots)
                if slots:
                    # Бронируем и выходим
                    first = slots[0]
                    try:
                        book = await client.post("/select_slot", json={
                            "email": email,
                            "country": country,
                            "date": first["date"],
                            "time": first["time"],
                        }, cookies=cookies)
                        print("book status: ",book.status_code)
                    except httpx.ReadTimeout:
                        print("⏳ Таймаут при бронировании слота. Повторяем...")
                        try:
                            await bot.send_message(chat_id, text="Таймаут при бронировании. Повторяем поиск...")
                        except Exception as e:
                            print(f"❌ Ошибка при отправке сообщения: {e}")
                        await asyncio.sleep(60)
                        continue
                    except httpx.HTTPError as e:
                        print(f"❌ Ошибка HTTP при бронировании: {e}")
                        try:
                            await bot.send_message(chat_id, text=f"Ошибка при бронировании: {e}. Повторяем...")
                        except Exception as e:
                            print(f"❌ Ошибка при отправке сообщения: {e}")
                        await asyncio.sleep(60)
                        continue
                    if book.status_code == 200:
                        print("Слот нашёлся: ", first["date"], first["time"])
                        await bot.send_message(chat_id, text=f"Слот найден и забронирован: {first["date"]} {first["time"]}")
                        return
                    else:
                        try:
                            print(" мы здесь потому что ещё ищем слоты...внутри  try")
                            await bot.send_message(chat_id=chat_id, text ="Слот найден, но не удалось забронировать. Повторяем поиск... вунтри try")
                        except Exception as e:
                            print(" сообщение не отправилось в чат телеграмм..")
                            print(f"❌ Ошибка при отправке сообщения: {e}")

                else:
                    print(" мы здесь потому что ещё ищем слоты...")
                    await bot.send_message(chat_id=chat_id, text="мы здесь потому что ещё ищем слоты...")


        await asyncio.sleep(60)
