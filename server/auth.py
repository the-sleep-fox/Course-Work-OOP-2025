
from fastapi import APIRouter, HTTPException, Depends, Response, Request
from sqlalchemy.orm import Session
from server.database import get_db
from server.models.user import User
from .base_models import UserLogin, RegisterRequest
import uuid
import logging
from datetime import datetime

router = APIRouter()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Временное хранилище сессий
SESSIONS = {}

@router.post("/login")
def login(data: UserLogin, response: Response, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        logger.warning(f"Попытка входа с несуществующим email: {data.email}")
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    if not user.verify_password(data.password):
        logger.warning(f"Неверный пароль для {data.email}")
        raise HTTPException(status_code=401, detail="Неверный пароль")

    # Удаляем старую сессию, если существует
    old_session_id = request.cookies.get("session_id")
    if old_session_id and old_session_id in SESSIONS:
        logger.info(f"Удаление старой сессии для {data.email}: {old_session_id}")
        del SESSIONS[old_session_id]

    # Создаем новую сессию
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "email": data.email,
        "created_at": datetime.utcnow().isoformat()
    }
    logger.info(f"Создана сессия для {data.email}: {session_id}")
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # Отключено для локальной разработки без HTTPS
        samesite="strict",
        max_age=3600  # 1 час
    )
    return {"message": "Успешный вход", "user": data.email}

@router.post("/logout")
def logout(response: Response, request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in SESSIONS:
        email = SESSIONS[session_id]["email"]
        logger.info(f"Завершение сессии для {email}: {session_id}")
        del SESSIONS[session_id]
    response.delete_cookie("session_id")
    return {"message": "Выход успешен"}

@router.post("/register")
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        if not User.validate_passport(request.passport_id):
            logger.warning(f"Неверный формат паспорта: {request.passport_id}")
            raise HTTPException(status_code=400, detail="Неверный формат номера паспорта. Ожидается формат: AB1234567")
        if db.query(User).filter(User.email == request.email).first():
            logger.warning(f"Попытка регистрации с существующим email: {request.email}")
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
        if db.query(User).filter(User.passport_id == request.passport_id).first():
            logger.warning(f"Попытка регистрации с существующим паспортом: {request.passport_id}")
            raise HTTPException(status_code=400, detail="Пользователь с таким номером паспорта уже существует")

        user = User(
            passport_id=request.passport_id.upper(),
            email=request.email,
        )
        user.set_password(request.password)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Пользователь зарегистрирован: {request.email}")
        return {"message": "Пользователь успешно зарегистрирован"}
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при регистрации: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при регистрации: {str(e)}")