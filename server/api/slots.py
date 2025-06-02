from fastapi import APIRouter
from ..slot_store import available_slots  # или откуда у тебя actual data

router = APIRouter()

@router.get("/{country}/slots")
def get_slots(country: str):
    filtered = [slot for slot in available_slots if slot["country"] == country.lower()]
    return {"slots": filtered}
