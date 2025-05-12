from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: str
    password: str

class Slot(BaseModel):
    date: str
    available: bool
