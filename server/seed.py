#
from zoneinfo import available_timezones

from database import SessionLocal, init_db

from models.slot import Slot
#
init_db()
db = SessionLocal()
#
 # USERS
# users = {
#     "petusokalesa@gmail.com": "12345678",
#     "admin@gmail.com": "1111111",
#     "petushokalesia@gmail.com": "1234567"
# }
#
# for email, password in users.items():
#     user = User(email=email, passport_id="AA" + password)
#     user.set_password(password)
#     db.add(user)
#
# # SLOTS
available_slots = {
    "usa": [
        ("2025-06-07", "09:30"),
        ("2025-06-09", "16:00"),
        ("2025-06-12", "11:00"),
        ("2025-06-14", "13:30"),
        ("2025-06-16", "10:15"),
        ("2025-06-18", "15:00"),
        ("2025-06-20", "09:45")
    ],
    "poland": [
        ("2025-06-08", "10:15"),
        ("2025-06-10", "08:45"),
        ("2025-06-13", "12:00"),
        ("2025-06-15", "14:30"),
        ("2025-06-17", "09:15"),
        ("2025-06-19", "11:00"),
        ("2025-06-21", "16:00")
    ]
}
# #
for country, slot_list in available_slots.items():
    for date, time in slot_list:
        slot = Slot(country=country, date=date, time=time)
        db.add(slot)
#
db.commit()
db.close()
