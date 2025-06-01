from typing import cast
from fastapi import APIRouter, HTTPException, Depends
from server.models.slot import Slot
from server.models.booking import Booking
from server.models.user import User
from .base_models import SlotSelectionRequest
from .database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

from .my_email import send_notification_email


# from .seed import country

router = APIRouter()

# available_slots = {
#     "usa": [("2025-06-01", "10:00"), ("2025-06-03", "12:00")],
#     "poland": [("2025-06-02", "09:00"), ("2025-06-04", "11:30")]
# }



@router.get("/{country}/slots")
def get_slots(country: str):
    from .slot_store import available_slots
    filtered = [slot for slot in available_slots if slot["country"] == country.lower()]
    return {"slots": filtered}

@router.post("/select_slot")
def select_slot(request: SlotSelectionRequest, db: Session = Depends(get_db)):
    print("📩 Запрос получен:", request.model_dump())

    # Проверка: существует ли пользователь
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        print("❌ Пользователь не найден:", request.email)
        raise HTTPException(status_code=404, detail="User not found")

    # Проверка: доступен ли слот
    slot = db.query(Slot).filter_by(
        date=request.date,
        time=request.time,
        country=request.country
    ).first()

    if not slot:
        print("❌ Слот не найден:", request.date, request.time, request.country)
        raise HTTPException(status_code=404, detail="Slot not available")

    # Проверка: есть ли уже бронь у пользователя в этой стране
    existing_booking = db.query(Booking).filter_by(
        email=request.email,
        country=request.country
    ).first()

    if existing_booking:
        print(f"⚠️ {request.email} уже записан в {request.country}")
        raise HTTPException(status_code=400, detail="User already booked a slot for this country")

    # ✅ Создание новой брони
    booking = Booking(
        email=request.email,
        country=request.country,
        date=request.date,
        time=request.time
    )

    db.add(booking)
    db.delete(slot)
    db.commit()

    try:
        send_notification_email(request.email, request.country, (request.date, request.time))
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

    return {
        "message": "Слот успешно забронирован и письмо отправлено",
        "slot": (request.date, request.time)
    }

    print(f"✅ Слот забронирован: {request.email} -> {request.country} {request.date} {request.time}")
    return {"message": "Slot booked successfully"}



@router.delete("/cancel_booking")
def cancel_booking(email: str, country: str,  db: Session = Depends(get_db)):
    booking = cast(Booking, db.query(Booking).filter_by(email=email, country=country).first())
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.date > str(datetime.now().date()) and booking.time > str(datetime.now().time()):
        from server.models.slot import Slot
        slot = Slot(date=booking.date, time=booking.time, country=booking.country)
        db.add(slot)
    else:
        from server.models.slot import Slot
        slot = Slot(date=booking.date, time=booking.time, country=booking.country)
        db.delete(booking)
        db.commit()
        print("Слот для времени на визу просрочен")
    return {"message": "Booking cancelled and slot returned to availability"}




@router.get("/get_bookings")
def get_bookings(email: str, db: Session = Depends(get_db)):
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