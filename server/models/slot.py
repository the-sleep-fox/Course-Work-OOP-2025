from sqlalchemy import Column, Integer, String
from server.database import Base

class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, nullable=False)
    date = Column(String, nullable=False) #ИЗМЕНИТЬ ТИП НА ДАТА И ВРЕМЯ -- проще будет
    time = Column(String, nullable=False)