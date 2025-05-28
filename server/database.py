from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./db.sqlite3"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

users = {
    "petusokalesa@gmail.com": "1234567",
    "admin@gmail.com": "1111111",
    "petushokalesia@gmail.com": "1234567"

}

slots = [
    {"date": "2025-05-14", "available": False},
    {"date": "2025-05-18", "available": True},
]