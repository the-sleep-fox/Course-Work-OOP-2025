from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from server.database import get_db, SessionLocal
from server.models.user import User
from .base_models import UserLogin, RegisterRequest

router = APIRouter()

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    if not user.verify_password(data.password):
        raise HTTPException(status_code=401, detail="Неверный пароль")

    return {"message": "Успешный вход", "user": data.email}

@router.post("/register")
async def register_user(request: RegisterRequest):
    db = SessionLocal()
    try:
        # Проверка валидности паспорта
        if not User.validate_passport(request.passport_id):
            raise HTTPException(status_code=400, detail="Неверный формат номера паспорта. Ожидается формат: AB1234567")

        # Проверка уникальности email
        if db.query(User).filter(User.email == request.email).first():
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

        # Проверка уникальности passport_id
        if db.query(User).filter(User.passport_id == request.passport_id).first():
            raise HTTPException(status_code=400, detail="Пользователь с таким номером паспорта уже существует")

        # Создание нового пользователя
        user = User(
            passport_id=request.passport_id.upper(),
            email=request.email,
        )
        user.set_password(request.password)  # Хешируем пароль

        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "Пользователь успешно зарегистрирован"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при регистрации: {str(e)}")
    finally:
        db.close()