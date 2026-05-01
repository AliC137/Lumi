"""
schemas/user_update.py

Pydantic schema for updating user information.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    login: Optional[EmailStr] = Field(None, description="User email/login")
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="User name")
    password: Optional[str] = Field(None, min_length=6, max_length=255, description="User password (will be hashed)")
    role: Optional[str] = Field(None, description="User role (user/admin)")

