
from typing import cast
from fastapi import APIRouter, HTTPException, Depends, Request
from server.models.slot import Slot
from server.models.booking import Booking
from server.models.user import User
from .base_models import SlotSelectionRequest
from .database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from .my_email import send_notification_email
from .slots_scheduler import refresh_slots

router = APIRouter()

@router.get("/{country}/slots")
def get_slots(country: str, request: Request, db: Session = Depends(get_db)):
    user_email = request.state.user_email  # Извлекаем email из сессии
    from .slot_store import available_slots
    filtered = [slot for slot in available_slots if slot["country"] == country.lower()]
    return {"slots": filtered}

@router.post("/select_slot")
def select_slot(request: SlotSelectionRequest, request_state: Request, db: Session = Depends(get_db)):
    print("📩 Запрос получен:", request.model_dump())
    user_email = request_state.state.user_email  # Извлекаем email из сессии

    # Проверка: email в запросе должен совпадать с авторизованным пользователем
    if request.email != user_email:
        print(f"Несанкционированная попытка бронирования: {request.email} != {user_email}")
        raise HTTPException(status_code=403, detail="Cannot book for another user")

    # Проверка: существует ли пользователь
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        print("Пользователь не найден:", request.email)
        raise HTTPException(status_code=404, detail="User not found")

    # Проверка: существует ли слот
    slot = db.query(Slot).filter_by(
        date=request.date,
        time=request.time,
        country=request.country
    ).first()
    if not slot:
        print("Слот не найден:", request.date, request.time, request.country)
        raise HTTPException(status_code=404, detail="Slot not available")


    existing_booking = db.query(Booking).filter_by(
        email=request.email,
        country=request.country
    ).first()
    if existing_booking:
        print(f"{request.email} уже записан в {request.country}")
        raise HTTPException(status_code=400, detail="User already booked a slot for this country")


    booking = Booking(
        email=request.email,
        country=request.country,
        date=request.date,
        time=request.time
    )
    db.add(booking)
    db.delete(slot)
    db.commit()
    refresh_slots()
    try:
        send_notification_email(request.email, request.country, (request.date, request.time))
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

    return {
        "message": "Слот успешно забронирован и письмо отправлено",
        "slot": (request.date, request.time)
    }

@router.delete("/cancel_booking")
def cancel_booking(email: str, country: str, request: Request, db: Session = Depends(get_db)):
    user_email = request.state.user_email


    if email != user_email:
        print(f"Несанкционированная попытка отмены: {email} != {user_email}")
        raise HTTPException(status_code=403, detail="Cannot cancel booking for another user")

    booking = cast(Booking, db.query(Booking).filter_by(email=email, country=country).first())
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")


    slot = Slot(date=booking.date, time=booking.time, country=booking.country)
    if booking.date > str(datetime.now().date()) and booking.time > str(datetime.now().time()):
        db.delete(booking)
        db.add(slot)
        db.commit()
    else:
        db.delete(booking)
        db.commit()
        print("Слот для времени на визу просрочен")

    return {"message": "Booking cancelled and slot returned to availability"}

@router.get("/get_bookings")
def get_bookings(email: str, request: Request, db: Session = Depends(get_db)):
    user_email = request.state.user_email  # Извлекаем email из сессии

    # Проверка: email в запросе должен совпадать с авторизованным пользователем
    if email != user_email:
        print(f"Несанкционированная попытка просмотра: {email} != {user_email}")
        raise HTTPException(status_code=403, detail="Cannot view bookings for another user")

    bookings = db.query(Booking).filter_by(email=email).all()
    if not bookings:
        return {"bookings": []}

    result = []
    for booking in bookings:
        result.append({
            "country": booking.country,
            "date": booking.date,
            "time": booking.time
        })
    return {"bookings": result}

@router.post("/clear_slots")
def clear_slots(request: Request):
    user_email = request.state.user_email  # Извлекаем email из сессии

    # Временное отключение или ограничение доступа
    # Например, разрешить только админам (нужна дополнительная логика)
    raise HTTPException(status_code=403, detail="This endpoint is disabled for security reasons")

    # Если решите оставить, добавьте проверку прав
    # from .slot_store import available_slots
    # available_slots.clear()
    # print("Слоты очищены:", available_slots)
    # return {"message": "Слоты успешно очищены", "slots": available_slots}