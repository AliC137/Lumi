"""
api/v1/admin/schemas.py

Pydantic schemas for admin panel API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AdminInfo(BaseModel):
    """Schema for admin user information"""
    user_id: int
    login: str
    name: str
    role: str
    created_dt: datetime
    
    class Config:
        from_attributes = True


class AdminVerifyResponse(BaseModel):
    """Response schema for admin token verification"""
    valid: bool
    message: str
    admin_info: Optional[AdminInfo] = None


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items per page")


class PaginatedResponse(BaseModel):
    """Base schema for paginated responses"""
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool

