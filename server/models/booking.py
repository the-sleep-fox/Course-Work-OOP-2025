# booking.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from server.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    email = Column(String, ForeignKey("users.email"),nullable=False)
    country = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)

    user = relationship("User", back_populates="bookings")
