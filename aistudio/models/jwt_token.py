"""
models/jwt_token.py

Содержит описание модели JWT токенов для работы с базой данных (SQLAlchemy ORM).
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from aistudio.core.database import Base


class JWTToken(Base):
    __tablename__ = "jwt_tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_token = Column(String(1000), nullable=False)  # JWT access token
    refresh_token = Column(String(1000), nullable=False)  # JWT refresh token
    access_token_expired_time = Column(DateTime(timezone=True), nullable=False)
    refresh_token_expired_time = Column(DateTime(timezone=True), nullable=False)
    created_dt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_dt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_dt = Column(DateTime(timezone=True), nullable=True)
    
    # Связь с пользователем
    user = relationship("User", back_populates="tokens") 