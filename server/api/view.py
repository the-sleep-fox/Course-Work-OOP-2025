from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.models.booking import Booking
from ..database import get_db

router = APIRouter()

@router.get("/get_bookings")
def get_bookings(email: str, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter_by(email=email).all()
    return {
        "bookings": [
            {"country": b.country, "date": b.date, "time": b.time}
            for b in bookings
        ]
    }
