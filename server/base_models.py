from pydantic import BaseModel, EmailStr, Field


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

class CancelRequest(BaseModel):
    email: str
    country: str

class RegisterRequest(BaseModel):
    email: str
    passport_id: str = Field(..., pattern=r"^[A-Z]{2}\d{7}$")
    password: str = Field(..., min_length=8)