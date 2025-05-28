from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Slot(BaseModel):
    date: str
    available: bool

class SlotSelectionRequest(BaseModel):
    date: str
    time: str
    email: str
    country: str