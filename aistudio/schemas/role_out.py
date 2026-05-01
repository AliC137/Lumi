from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class RoleOut(BaseModel):
    """
    Схема для вывода роли
    """
    id: int = Field(..., description="Идентификатор роли")
    name: str = Field(..., description="Наименование роли")
    slug: str = Field(..., description="Обозначение роли")
    created_dt: Optional[datetime] = Field(None, description="Время создания")
    updated_dt: Optional[datetime] = Field(None, description="Время обновления")
    deleted_dt: Optional[datetime] = Field(None, description="Время удаления")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Владелец",
                "slug": "owner",
                "created_dt": "2024-01-01T00:00:00",
                "updated_dt": "2024-01-01T00:00:00",
                "deleted_dt": None
            }
        } 