"""
core/database.py

Настраивает подключение к базе данных и предоставляет доступ к сессиям SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError("Database configuration is incomplete. Check your .env file.")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD or '')}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency for database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
