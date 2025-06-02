from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from server.database import SessionLocal
from server.models import Slot
from server.slot_store import available_slots

def refresh_slots():
    print("🔄 Обновление слотов началось...")
    db = SessionLocal()
    try:
        slots = db.query(Slot).order_by(Slot.date, Slot.time).all()
        available_slots.clear()
        available_slots.extend([
            {
                "date": datetime.strptime(s.date, "%Y-%m-%d").strftime("%Y-%m-%d"),
                "time": datetime.strptime(s.time, "%H:%M").strftime("%H:%M"),
                "country": s.country
            }
            for s in slots
        ])
        print("Всего слотов в базе:", len(slots))
        print("💾 Загружено слотов:", available_slots)
    except Exception as e:
        print(f"❌ Ошибка при обновлении слотов: {e}")
    finally:
        db.close()

try:
    # Инициализация планировщика
    scheduler = BackgroundScheduler()
    # Вычисляем время запуска
    run_time = datetime.now() + timedelta(minutes=2)
    print(f"Планировщик настроен для запуска refresh_slots в {run_time}")
    # Запускаем refresh_slots один раз через 2 минуты
    scheduler.add_job(refresh_slots, 'date', run_date=run_time)
    print("Планировщик стартует...")
    scheduler.start()
    print("Планировщик запущен успешно")
except Exception as e:
    print(f"❌ Ошибка при запуске планировщика: {e}")