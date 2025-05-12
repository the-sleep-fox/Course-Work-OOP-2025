from fastapi import APIRouter
from models import Slot
from database import slots

router = APIRouter()

@router.get("/next", response_model=Slot)
def get_next_available():
    for slot in slots:
        if slot["available"]:
            return slot
    return {"date": "нет доступных дат", "available": False}
