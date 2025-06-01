from datetime import datetime
from server.database import SessionLocal
from server.models import Slot


def refresh_slots():
    print("🔄 Обновление слотов началось...")
    from .slot_store import available_slots
    global available_slots
    db = SessionLocal()
    slots = (
        db.query(Slot)
        .order_by(Slot.date, Slot.time)
        .all()
    )
    available_slots.clear()
    available_slots.extend( [
        {
            "date": datetime.strptime(s.date, "%Y-%m-%d").strftime("%Y-%m-%d"),
            "time": datetime.strptime(s.time, "%H:%M").strftime("%H:%M"),
            "country": s.country
        }
        for s in slots
    ])
    print("Всего слотов в базе:", len(slots))
    print("💾 Загружено слотов:", available_slots)
    db.close()

# scheduler = BackgroundScheduler()
# scheduler.add_job(refresh_slots, "interval", minutes=1)
# scheduler.start()