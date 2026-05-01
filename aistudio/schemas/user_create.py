"""
schemas/user_create.py

Содержит Pydantic-схемы для валидации входных данных, связанных с пользователями.
"""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    login: EmailStr = Field(...)
    name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=255)
