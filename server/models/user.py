from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
import re
from server.database import Base

# Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    passport_id = Column(String(9), primary_key=True, unique=True, index=True)  # Пример: AB1234567
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    bookings = relationship("Booking", back_populates="user", uselist=False)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def validate_passport(passport_id: str) -> bool:
        return re.match(r"^[A-Z]{2}\d{7}$", passport_id.upper()) is not None
