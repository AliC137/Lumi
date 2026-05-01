"""
schemas/user_login.py

Содержит Pydantic-схемы для валидации входных данных, связанных с пользователями.
"""

from pydantic import BaseModel, EmailStr, Field


class ProfileRequest(BaseModel):
    profile_id: int = Field(...)
    question: str = Field(...)
    session_id: str = Field(..., min_length=6, max_length=255)
