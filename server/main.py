from fastapi import FastAPI, Request, HTTPException
from server.auth import router as auth_router
from server import slots
from server.database import init_db

app = FastAPI(title="Visa Slot Server")

# Подключаем роутеры
app.include_router(auth_router, prefix="/auth")
app.include_router(slots.router)

# Инициализация базы данных
init_db()

# Временное хранилище сессий (из auth.py)
from server.auth import SESSIONS

@app.middleware("http")
async def check_session(request: Request, call_next):
    # Пропускаем публичные эндпоинты
    if request.url.path in ["/auth/login", "/auth/register"]:
        return await call_next(request)
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=401, detail="Не авторизован")
    request.state.user_email = SESSIONS[session_id]["email"]
    return await call_next(request)

@app.get("/")
def root():
    return "Добро пожаловать! Войдите или зарегистрируйтесь."