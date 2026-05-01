"""
schemas/user_login.py

Содержит Pydantic-схемы для валидации входных данных, связанных с пользователями.
"""

from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    login: EmailStr = Field(...)
    password: str = Field(..., min_length=6, max_length=255)
