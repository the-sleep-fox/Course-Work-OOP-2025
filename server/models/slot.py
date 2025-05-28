from sqlmodel import SQLModel, Field
from typing import Optional

class Slot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    country: str
    date: str
    time: str
