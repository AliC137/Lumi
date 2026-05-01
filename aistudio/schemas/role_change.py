"""
schemas/role_change.py

Схемы для изменения роли пользователя.
"""

from pydantic import BaseModel, Field

class RoleChangeRequest(BaseModel):
    """Схема для запроса изменения роли пользователя."""
    role: str = Field(..., description="Новая роль пользователя", example="admin") 