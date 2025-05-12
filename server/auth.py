from fastapi import APIRouter, HTTPException
from models import UserLogin
from database import users

router = APIRouter()

@router.post("/login")
def login(data: UserLogin):
    if users.get(data.email) == data.password:
        return {"message": "Успешный вход", "user": data.email}
    raise HTTPException(status_code=401, detail="Неверные логин или пароль")
