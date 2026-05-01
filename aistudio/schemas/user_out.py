"""
schemas/user_out.py

Содержит Pydantic-схемы для валидации выходных данных, связанных с пользователями.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserOut(BaseModel):
    """Basic user output schema for general API responses"""
    id: int
    login: EmailStr
    name: str
    role: str
    is_active: bool = True
    created_dt: datetime
    updated_dt: datetime

    model_config = {
        "from_attributes": True
    }


class UserDetailOut(BaseModel):
    """Detailed user output schema with additional fields for admin panel"""
    id: int
    login: EmailStr
    name: str
    role: str
    is_active: bool = True
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_dt: datetime
    updated_dt: datetime
    deleted_dt: Optional[datetime] = Field(None, description="Soft delete timestamp")
    
    # Computed fields
    account_status: str = Field(default="active", description="Human-readable account status")
    days_since_creation: int = Field(default=0, description="Days since account creation")
    days_since_last_login: Optional[int] = Field(None, description="Days since last login")
    
    model_config = {
        "from_attributes": True
    }
    
    @classmethod
    def from_user(cls, user):
        """Create UserDetailOut from User model with computed fields"""
        from datetime import datetime, timezone
        
        # Calculate account status
        if user.deleted_dt:
            account_status = "deleted"
        elif not user.is_active:
            account_status = "inactive"
        else:
            account_status = "active"
        
        # Calculate days since creation
        now = datetime.now(timezone.utc)
        created = user.created_dt
        if created.tzinfo is None:
            from datetime import timezone as tz
            created = created.replace(tzinfo=tz.utc)
        
        days_since_creation = (now - created).days
        
        # Calculate days since last login
        days_since_last_login = None
        if user.last_login:
            last_login = user.last_login
            if last_login.tzinfo is None:
                from datetime import timezone as tz
                last_login = last_login.replace(tzinfo=tz.utc)
            days_since_last_login = (now - last_login).days
        
        return cls(
            id=user.id,
            login=user.login,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            last_login=user.last_login,
            created_dt=user.created_dt,
            updated_dt=user.updated_dt,
            deleted_dt=user.deleted_dt,
            account_status=account_status,
            days_since_creation=days_since_creation,
            days_since_last_login=days_since_last_login
        )

