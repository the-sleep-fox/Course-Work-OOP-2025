from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.user import User
from .base_models import UserLogin

router = APIRouter()

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    if not user.verify_password(data.password):
        raise HTTPException(status_code=401, detail="Неверный пароль")

    return {"message": "Успешный вход", "user": data.email}