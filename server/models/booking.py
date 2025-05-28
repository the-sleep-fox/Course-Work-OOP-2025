from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

from server.models.slot import Slot
from server.models.user import User


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    slot_id: int = Field(foreign_key="slot.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="bookings")
    slot: Optional[Slot] = Relationship(back_populates="bookings")
