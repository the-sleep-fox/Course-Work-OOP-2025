#
from zoneinfo import available_timezones

from .database import SessionLocal, init_db
# from .models.user import User
from .models.slot import Slot
#
# init_db()
# db = SessionLocal()
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
# available_slots = {
#     "usa": [
#         ("2025-06-01", "10:00"),
#         ("2025-06-03", "12:00"),
#         ("2025-06-05", "14:00"),
#         ("2025-06-07", "09:30"),
#         ("2025-06-09", "16:00")
#     ],
#     "poland": [
#         ("2025-06-02", "09:00"),
#         ("2025-06-04", "11:30"),
#         ("2025-06-06", "13:45"),
#         ("2025-06-08", "10:15"),
#         ("2025-06-10", "08:45")
#     ]
# }
# #
# for country, slot_list in available_slots.items():
#     for date, time in slot_list:
#         slot = Slot(country=country, date=date, time=time)
#         db.add(slot)
# #
# db.commit()
# db.close()
