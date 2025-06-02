from fastapi import FastAPI, APIRouter
from .auth import router as auth_router
from . import slots
from server.database import init_db
from .models import booking
from .slots_scheduler import refresh_slots
from .slots import clear_slots
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI(title="Visa Slot Server")

     # Подключаем роутер для авторизации
app.include_router(auth_router, prefix="/auth")

# Подключаем роутер для слотов
app.include_router(slots.router)

     # Инициализация базы данных
init_db()

     # Определяем новый роутер для дополнительных эндпоинтов
extra_router = APIRouter()

@extra_router.post("/clear_slots")
def clear_slots_endpoint():
    from .slot_store import available_slots
    clear_slots()
    return {"message": "Слоты успешно очищены", "slots": available_slots}

     # Подключаем дополнительный роутер
app.include_router(extra_router)

@app.get("/")
def root():
    return "Добро пожаловать! Войдите или зарегистрируйтесь."

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