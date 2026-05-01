"""
schemas/refresh_token.py

Содержит Pydantic-схемы для валидации данных refresh токенов.
"""

from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token for getting new access token")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer" 