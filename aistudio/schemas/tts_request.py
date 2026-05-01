"""
schemas/user_login.py

Содержит Pydantic-схемы для валидации входных данных, связанных с пользователями.
"""

from pydantic import BaseModel, EmailStr, Field


class TTSRequest(BaseModel):
    text: str = Field(...)
