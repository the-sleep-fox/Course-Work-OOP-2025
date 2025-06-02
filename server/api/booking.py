from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from server.models.booking import Booking
from server.models.slot import Slot
from server.models.user import User
from ..base_models import SlotSelectionRequest
from ..database import get_db
from ..my_email import send_notification_email
from datetime import datetime
from typing import cast

router = APIRouter()

@router.post("/select_slot")
def select_slot(request: SlotSelectionRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    slot = db.query(Slot).filter_by(
        date=request.date,
        time=request.time,
        country=request.country
    ).first()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not available")

    existing_booking = db.query(Booking).filter_by(
        email=request.email,
        country=request.country
    ).first()

    if existing_booking:
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

    try:
        send_notification_email(request.email, request.country, (request.date, request.time))
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

    return {
        "message": "Слот успешно забронирован и письмо отправлено",
        "slot": (request.date, request.time)
    }

@router.delete("/cancel_booking")
def cancel_booking(email: str, country: str, db: Session = Depends(get_db)):
    booking = cast(Booking, db.query(Booking).filter_by(email=email, country=country).first())
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.date > str(datetime.now().date()) and booking.time > str(datetime.now().time()):
        db.add(Slot(date=booking.date, time=booking.time, country=booking.country))
    else:
        db.delete(booking)
        db.commit()
        print("Слот для времени на визу просрочен")

    return {"message": "Booking cancelled and slot returned to availability"}
