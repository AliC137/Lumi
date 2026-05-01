"""
models/user.py

Содержит описание модели пользователя для работы с базой данных (SQLAlchemy ORM).
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from aistudio.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(255), unique=True, nullable=False, index=True)  # Email
    name = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)  # Hashed password
    role = Column(String(20), nullable=False, default="user")  # Role field
    is_active = Column(Boolean, nullable=False, default=True)  # Active status
    last_login = Column(DateTime(timezone=True), nullable=True)  # Last login timestamp
    created_dt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_dt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_dt = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    tokens = relationship("JWTToken", back_populates="user")
