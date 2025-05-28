from fastapi import FastAPI
from auth import router as auth_router
import slots

app = FastAPI(title="Visa Slot Server")

app.include_router(auth_router, prefix="/auth")
# app.include_router(slot_router, prefix="/slots")

app.include_router(slots.router)
@app.get("/")
def root():
    return "Добро пожаловать! Войдите или зарегистрируйтесь."
