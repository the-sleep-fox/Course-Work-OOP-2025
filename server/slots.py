from fastapi import APIRouter, HTTPException
from my_email import send_notification_email
from models import SlotSelectionRequest

router = APIRouter()

available_slots = {
    "usa": [("2025-06-01", "10:00"), ("2025-06-03", "12:00")],
    "poland": [("2025-06-02", "09:00"), ("2025-06-04", "11:30")]
}


reserved_slots = {}

@router.get("/{country}/slots")
async def get_slots(country: str):
    country = country.lower()
    if country not in available_slots:
        raise HTTPException(status_code=404, detail="Страна не найдена")
    return {"slots": available_slots[country]}


@router.post("/select_slot")
async def select_slot(data: SlotSelectionRequest):
    date = data.date
    time = data.time
    email = data.email
    country = data.country

    if not email or not country or not date or not time:
        raise HTTPException(status_code=400, detail="Неверные данные")

    slots = available_slots.get(country.lower())
    if not slots or (date, time) not in slots:
        raise HTTPException(status_code=404, detail="Нет подходящего слота")

    slots.remove((date, time))
    reserved_slots[email] = {"country": country, "slot": (date, time)}

    # Notification by mail
    try:
        send_notification_email(email, country, (date, time))
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

    return {
        "message": "Слот успешно забронирован и письмо отправлено",
        "slot": (date, time)
    }